import sublime
import sublime_plugin
import os
import re
import fnmatch
import json

from ..ml_utils import MlUtils

class MarkLogicAutoComplete(sublime_plugin.EventListener):

	def __init__(self):
		self.dynamic_snippets = None
		self.function_snippets = None

	# caches a list of dynamic snippets
	def gen_dynamic_snippets(self):
		if (self.dynamic_snippets == None):
			self.dynamic_snippets = []
			snip_dir = sublime.packages_path() + "/MarkLogic-Sublime/dynamic_snippets/"
			for root, dirnames, filenames in os.walk(snip_dir):
				for filename in fnmatch.filter(filenames, '*.json'):
					fn = os.path.join(root, filename)
					with open(fn, 'r') as f:
						self.dynamic_snippets.append(self.create_snippet_object(json.load(f)))

	# load the builtin function snippets from disk
	def gen_function_snippets(self):
		if (self.function_snippets == None):
			self.function_snippets = []

			functions_file = sublime.packages_path() + "/MarkLogic-Sublime/marklogic_builtins/ml-functions.json"
			with open(functions_file, 'r') as f:
				for s in json.load(f):
					self.function_snippets.append(self.create_snippet_object(s))

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
	def process_function_snippets(self, view, prefix, completions):
		self.gen_function_snippets()

		if MlUtils.get_sub_pref("autocomplete", "enable_marklogic_functions") == True:
			for snip in self.function_snippets:
				trigger = snip['trigger']
				if (prefix in trigger):
					content = snip['content']
					completions.append((snip['completion'], content))

	# called when Sublime wants a list of autocompletes
	def on_query_completions(self, view, prefix, locations):
		completions = []

		if view.match_selector(locations[0], "source.xquery-ml"):
			self.process_dynamic_snippets(view, prefix, completions)
			self.process_function_snippets(view, prefix, completions)

		return completions