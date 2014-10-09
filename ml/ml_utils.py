import sublime
import os

from .ml_settings import MlSettings

SETTINGS_FILE = "MarkLogic.sublime-settings"

class MlUtils:
	@staticmethod
	def log(log_me):
		if (MlSettings.debug()):
			print(log_me)

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
