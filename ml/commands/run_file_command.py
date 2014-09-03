import sublime
import sublime_plugin

from ..xcc import Xcc

class RunFileCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		contents = self.view.substr(sublime.Region(0, self.view.size()))
		xcc = Xcc()
		resp = xcc.run_query(contents)
		self.show_output_panel(edit, resp)

	def show_output_panel(self, edit, txt):
		window = self.view.window()
		if not hasattr(self, 'output_view'):
			self.output_view = window.get_output_panel("ml_run_output")

		self.output_view.erase(edit, sublime.Region(0, self.output_view.size()))
		self.output_view.insert(edit, self.output_view.size(), txt)
		window.run_command("show_panel", {"panel": "output.ml_run_output"})