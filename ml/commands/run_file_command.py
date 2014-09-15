import sublime
import sublime_plugin
import sys

if sys.version_info >= (3,):
	from urllib.error import URLError
else:
	from urllib2 import URLError

from ..xcc import Xcc

class RunFileCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		contents = self.view.substr(sublime.Region(0, self.view.size()))
		try:
			xcc = Xcc()
			resp = xcc.run_query(contents)
			self.show_output_panel(edit, resp)
		except URLError as e:
			status = str(e.reason) + " %s" % xcc.base_url
			self.show_output_panel(edit, status)
		except Exception as e:
			status = str(e)
			self.show_output_panel(edit, status)

	def show_output_panel(self, edit, txt):
		window = self.view.window()
		self.output_view = window.get_output_panel("ml_run_output")
		self.output_view.erase(edit, sublime.Region(0, self.output_view.size()))
		self.output_view.insert(edit, self.output_view.size(), txt)
		window.run_command("show_panel", {"panel": "output.ml_run_output"})