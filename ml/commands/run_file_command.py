import sublime
import sublime_plugin
import sys
import re

if sys.version_info >= (3,):
	from urllib.error import URLError
else:
	from urllib2 import URLError

from ..xcc import Xcc
from ..ml_utils import MlUtils

class RunFileCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		contents = self.view.substr(sublime.Region(0, self.view.size()))
		try:
			xcc = Xcc()
			query_type = "xquery"
			if MlUtils.is_server_side_js(self.view):
				query_type = "javascript"
			resp = xcc.run_query(contents, query_type)
			self.show_output_panel(edit, resp)
		except URLError as e:
			print(e)
			status = str(e.reason) + " %s" % xcc.base_url
			self.show_output_panel(edit, status)
		except Exception as e:
			print(e)
			status = str(e)
			self.show_output_panel(edit, status)

	def show_output_panel(self, edit, txt):
		window = self.view.window()
		self.output_view = window.get_output_panel("ml_run_output")
		self.output_view.erase(edit, sublime.Region(0, self.output_view.size()))
		self.output_view.insert(edit, self.output_view.size(), txt)
		window.run_command("show_panel", {"panel": "output.ml_run_output"})