import sublime, sublime_plugin

from ..ml_utils import MlUtils

class mlToggleLintCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.options = ['Lint on Save: On', 'Lint on Save: Off']
		self.window.show_quick_panel(self.options, self.on_done)

	def on_done(self, picked):
		value = self.options[picked]
		MlUtils.set_lint_on_save(value == 'Lint on Save: On')
