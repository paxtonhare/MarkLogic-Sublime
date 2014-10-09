import sublime, sublime_plugin

from ..ml_settings import MlSettings

class mlToggleLintCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.options = ['Lint on Save: On', 'Lint on Save: Off']
		self.window.show_quick_panel(self.options, self.on_done)

	def on_done(self, picked):
		if (picked >= 0):
			value = self.options[picked]
			MlSettings().set_lint_on_save(value == 'Lint on Save: On')
