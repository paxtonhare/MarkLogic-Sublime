import sublime
import os
import re

from .ml_settings import MlSettings

SETTINGS_FILE = "MarkLogic.sublime-settings"

class MlUtils:
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
	def get_function_defs(buffer, show_private):
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
			func = match[0]
			params = []
			pre_params = re.sub(r"[\r\n\s]+\$", "$", match[1])
			pre_params = re.sub(r"\)[\r\n\s]+as.*$", "", pre_params)
			if (len(pre_params) > 0):
				params = re.split(r",", pre_params)
			functions.append((func, params))

		return functions


	@staticmethod
	def get_imported_files(file_name, buffer):
		base_path = os.path.dirname(file_name)

		files = []
		for match in re.findall(r"import[\r\n\s]+module.*?at[\r\n\s]+['\"]([^'\"]+)['\"];?", buffer, re.DOTALL | re.M):
			path = os.path.join(base_path, match)
			if (os.path.exists(path)):
				files.append(path)

		return files

