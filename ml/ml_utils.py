import sublime
import os
import re

from .ml_settings import MlSettings

SETTINGS_FILE = "MarkLogic.sublime-settings"

class MlUtils:
	__module_import_regex__ = re.compile(r"import[\r\n\s]+module\s+((namespace\s+)?([^\s]+)\s*=\s*)?.*?at[\r\n\s]*['\"]([^'\"]+)['\"];?", re.M | re.DOTALL)
	@staticmethod
	def log(log_me):
		if (MlSettings.debug()):
			print("[MarkLogic]\t%s" % log_me)

	@staticmethod
	def load_resource(name):
		if hasattr(sublime, 'load_resource'):
			return sublime.load_resource(name)
		else:
			with open(os.path.join(sublime.packages_path(), name[9:])) as f:
				return f.read()

	@staticmethod
	def is_server_side_js(view):
		return view.score_selector(view.sel()[0].a, 'source.serverside-js') > 0

	@staticmethod
	def get_namespace(s):
		ns_str = r"""\s*xquery[^'\"]+(['\"])[^'\"]+?\1;?\s+module\s+namespace\s+([^\s]+)\s+=\s+(['\"])([^'\"]+)?\3"""
		ns_re = re.compile(ns_str)
		sans_comments = re.sub(r"\(:.*?:\)", "", s)
		match = ns_re.search(sans_comments)
		print("match: %s" % str(match))
		if (match):
			return (match.group(2), match.group(4))
		else:
			return (None, None)

	@staticmethod
	def get_function_defs(file_name, buffer, ns_prefix, show_private):
		functions = []

		if (show_private):
			private_re = ""
		else:
			private_re = "(?<!%private)"
		function_str = r"""%s # optional bit to exclude private functions
						   \s+
						   function[\s]+
						   (?!namespace)  # bail if it's a function namespace decl
						   ((?:[\-_a-zA-Z0-9]+:)?[\-_a-zA-Z0-9]+)   #function name part
						   \s*
						   \( # paren before parameters
						   \s*([^{]*)\s* # all the parameters
						   \) # paren after parameters
						""" % private_re
		function_re = re.compile(function_str, re.S | re.M | re.X)
		for match in function_re.findall(buffer, re.DOTALL | re.M | re.X):
			if ns_prefix and ns_prefix != '':
				func = re.sub(r"([^:]+:)?([^:]+)", "%s:\\2" % ns_prefix, match[0])
			else:
				func = re.sub(r"([^:]+:)?([^:]+)", "\\2", match[0])
			params = []
			pre_params = re.sub(r"[\r\n\s]+\$", "$", match[1])
			pre_params = re.sub(r"\)[\r\n\s]+as.*$", "", pre_params)
			if (len(pre_params) > 0):
				params = re.split(r",", pre_params)
			functions.append((func, params))

		return functions


	@staticmethod
	def get_imported_files(file_name, buffer):
		files = []
		search_paths = MlSettings().get_search_paths()

		if (search_paths):
			for match in MlUtils.__module_import_regex__.findall(buffer, re.DOTALL | re.M):
				ns_prefix = match[2]
				uri = match[3]
				for search_path in search_paths:
					if (uri[0] == '/'):
						f = os.path.join(search_path, uri[1:])
					else:
						f = os.path.join(os.path.dirname(file_name), uri)

					if (os.path.exists(f)):
						files.append((f, ns_prefix))

		return files

