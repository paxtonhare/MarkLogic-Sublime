import sublime, sublime_plugin

from ..ml_settings import MlSettings

class mlOpenOptionsCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.window.open_file(MlSettings().get_current_options_file())