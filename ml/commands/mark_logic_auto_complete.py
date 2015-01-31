import sublime
import sublime_plugin
import os
import re
import fnmatch
import json

from ..ml_utils import MlUtils
from ..ml_settings import MlSettings

class MarkLogicAutoComplete(sublime_plugin.EventListener):

	def __init__(self):
		self.dynamic_snippets = None
		self.xquery_function_snippets = []
		self.javascript_function_snippets = []

	# caches a list of dynamic snippets
	def gen_dynamic_snippets(self):
		if (self.dynamic_snippets == None):
			self.dynamic_snippets = []
			snip_dir = "Packages/MarkLogic/dynamic_snippets/"
			for filename in ["function.json", "imports.json"]:
				f = MlUtils.load_resource(os.path.join(snip_dir, filename))
				jo = json.loads(f)
				if isinstance(jo, list):
					for snip in jo:
						self.dynamic_snippets.append(self.create_snippet_object(snip))
				else:
					self.dynamic_snippets.append(self.create_snippet_object(jo))

	# load the builtin function snippets from disk
	def gen_function_snippets(self, snippets, filename):
		if (len(snippets) == 0):
			functions_file = "Packages/MarkLogic/marklogic_builtins/%s" % filename
			f = MlUtils.load_resource(functions_file)
			for s in json.loads(f):
				snippets.append(self.create_snippet_object(s))

	# creates a snippet object for storing in a cache
	def create_snippet_object(self, snip):
		completion = snip['trigger']
		if ('description' in snip):
			completion = completion + '\t' + snip['description']
		o = {
			'trigger': snip['trigger'],
			'completion': completion,
			'content': snip['content']
		}
		return o

	# get the namespace of the current xquery module
	def get_module_namespace(self, view):
		contents = view.substr(sublime.Region(0, view.size()))
		search = re.search(r"^\s*module\s+namespace\s+([^\s]+)\s+", contents, re.MULTILINE)
		if search != None:
			return search.groups()[0]
		return 'local'

	# add dynamic snippets to the autocomplete list
	def process_dynamic_snippets(self, view, prefix, completions):
		self.gen_dynamic_snippets()

		namespace = self.get_module_namespace(view)
		for snip in self.dynamic_snippets:
			trigger = snip['trigger']
			if (prefix in trigger):
				content = re.sub(r'%NS%', namespace, snip['content'])
				completions.append((snip['completion'], content))

	# add MarkLogic builtins to the autocomplete list
	def process_function_snippets(self, view, prefix, snippets, filename, completions):
		self.gen_function_snippets(snippets, filename)

		if MlSettings.enable_marklogic_functions() == True:
			for snip in snippets:
				trigger = snip['trigger']
				if (prefix in trigger):
					content = snip['content']
					completions.append((snip['completion'], content))

	def snippets_from_xqy_file(self, file_name, contents, ns_prefix, show_private, prefix, completions):
		for func in MlUtils.get_function_defs(file_name, contents, ns_prefix, show_private):
			trigger = func[0]
			if (prefix in trigger):
				description = "(%s)" % re.sub(r"\s+as[^,]+", "", ",".join(func[1]))
				completion = "%s\t%s" % (trigger, description)

				params = []
				index = 1
				for param in func[1]:
					params.append('${%d:\\%s}' % (index, param))
					index = index + 1

				content = "%s(%s)" % (trigger, ", ".join(params))
				completions.append((completion, content))

	def process_included_code_snippets(self, view, prefix, completions):
		contents = view.substr(sublime.Region(0, view.size()))
		file_name = view.file_name()
		ns_prefix, ns_uri = MlUtils.get_namespace(contents)
		self.snippets_from_xqy_file(file_name, contents, ns_prefix, True, prefix, completions)

		if (file_name):
			for other_file, ns_prefix in MlUtils.get_imported_files(file_name, contents):
				with open(other_file, "r") as myfile:
					buffer = myfile.read()
				self.snippets_from_xqy_file(other_file, buffer, ns_prefix, False, prefix, completions)

	# called when Sublime wants a list of autocompletes
	def on_query_completions(self, view, prefix, locations):
		completions = []

		if view.match_selector(locations[0], "source.xquery-ml"):
			self.process_dynamic_snippets(view, prefix, completions)
			self.process_function_snippets(view, prefix, self.xquery_function_snippets, 'ml-xquery-functions.json', completions)
			self.process_included_code_snippets(view, prefix, completions)
		elif MlUtils.is_server_side_js(view):
			self.process_function_snippets(view, prefix, self.javascript_function_snippets, 'ml-javascript-functions.json', completions)

		return completions