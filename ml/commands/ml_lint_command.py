import sublime
import sublime_plugin
import os, re
import functools
import sys

if sys.version_info >= (3,):
	from urllib.error import URLError
else:
	from urllib2 import URLError
from threading import Timer
from ..xcc import Xcc
from ..ml_utils import MlUtils

class mlLintCommand(sublime_plugin.TextCommand):
	def run(self, edit, show_regions=True, show_panel=True):
		if False == self.file_supported():
			return

		contents = self.view.substr(sublime.Region(0, self.view.size()))
		is_module = self.is_module(contents)
		if (is_module):
			contents = self.module_to_main(contents) + "\n()"
		try:
			xcc = Xcc()
			query_type = "xquery"
			if self.is_js_file:
				query_type = "javascript"
			resp = xcc.run_query(contents, query_type, True)

			# reset stuff
			mlErrorGlobalStore.reset()
			mlLintEventListeners.reset()
			self.view.erase_regions("marklogic_compile_errors")

			if self.has_error(resp):
				description, line, column = self.error_location(resp)
				regions = []
				menuitems = []
				hint_point = self.view.text_point(int(line) - 1, int(column))#int(line_no) - 1, int(column_no) - 1)
				hint_region = self.view.word(hint_point)

				regions.append(hint_region)
				menuitems.append(line + ":" + column + " " + description)
				mlErrorGlobalStore.errors.append((hint_region, description, self.view.file_name()))

				if show_regions:
					self.add_regions(regions)
				if show_panel:
					self.view.window().show_quick_panel(menuitems, self.on_quick_panel_selection)

				# display error on status bar
				status = line + ":" + column + " " + description
				sublime.set_timeout(functools.partial(self.updateStatus, status), 100)
		except URLError as e:
			# do this delayed becauase sublime will overwrite after a save
			status = str(e.reason) + " %s" % xcc.base_url
			sublime.set_timeout(functools.partial(self.updateStatus, status), 100)
		except Exception as e:
			status = str(e)
			sublime.set_timeout(functools.partial(self.updateStatus, status), 100)

	def updateStatus(self, status):
		sublime.status_message(status)

	def is_js_file(self):
		return (re.search("JavaScript", self.view.settings().get("syntax"), re.I) != None)

	def file_supported(self):
		file_path = self.view.file_name()
		view_settings = self.view.settings()
		has_xqy_syntax = (re.search("xquery-ml", view_settings.get("syntax"), re.I) != None)
		has_js_syntax = self.is_js_file()
		return (has_xqy_syntax or has_js_syntax)

	def has_error(self, s):
		return re.search(r"\<error:error", s, re.DOTALL | re.M) != None

	def error_location(self, s):
		match = re.search(r"error:format-string\>([^<]+)\<.+?error:line\>(\d+)\<.+?error:column\>(\d+)\<", s, re.DOTALL | re.M)
		if match:
			description = match.group(1)
			line = match.group(2)
			column = match.group(3)
			return (description, line, column)
		else:
			return None

	def module_to_main(self, s):
		return  re.sub(r"([\r\n\s]*xquery[^;]+;[\r\n\s]+)(module)", r"\1declare", s, re.DOTALL | re.M)

	def is_module(self, s):
		return re.search(r"[\r\n\s]*xquery[^;]+;[\r\n\s]+(module)", s, re.DOTALL | re.M) != None

	def add_regions(self, regions):
		if int(sublime.version()) >= 3000:
			icon = os.path.join("Packages", "MarkLogic", "icons", "error.png")
			self.view.add_regions("marklogic_compile_errors", regions, "keyword", icon,
				sublime.DRAW_EMPTY |
				sublime.DRAW_NO_FILL |
				sublime.DRAW_NO_OUTLINE |
				sublime.DRAW_SQUIGGLY_UNDERLINE)
		else:
			icon = os.path.join("..", "MarkLogic", "icons", "error")
			self.view.add_regions("marklogic_compile_errors", regions, "keyword", icon,
				sublime.DRAW_EMPTY |
				sublime.DRAW_OUTLINED)

		if MlUtils.get_sub_pref("lint", "scroll_to_error"):
			self.scroll_to_error(0)

	def scroll_to_error(self, index):
		if index == -1:
			return None

		# Focus the user requested region from the quick panel.
		region = mlErrorGlobalStore.errors[index][0]
		region_cursor = sublime.Region(region.begin(), region.begin())
		selection = self.view.sel()
		selection.clear()
		selection.add(region_cursor)
		self.view.show(region_cursor)
		return region

	def on_quick_panel_selection(self, index):
		if index == -1:
			return

		region = self.scroll_to_error(index)

		if not MlUtils.get_sub_pref("lint", "highlight_selected_regions"):
			return

		self.view.erase_regions("marklogic_lint_selected")
		self.view.add_regions("marklogic_lint_selected", [region], "meta")

class mlLintEventListeners(sublime_plugin.EventListener):
	timer = None

	@classmethod
	def reset(self):
		# Invalidate any previously set timer.
		if self.timer != None:
			self.timer.cancel()
			self.timer = None

	@classmethod
	def on_modified(self, view):
		# Continue only if the plugin settings allow this to happen.
		# This is only available in Sublime 3.
		if int(sublime.version()) < 3000:
			return
		if not MlUtils.get_sub_pref("lint", "lint_on_edit"):
			return

		# Re-run the ml_lint command after a second of inactivity after the view
		# has been modified, to avoid regions getting out of sync with the actual
		# previously linted source code.
		self.reset()

		timeout = MlUtils.get_sub_pref("lint", "lint_on_edit_timeout")
		self.timer = Timer(timeout, lambda: view.window().run_command("ml_lint", { "show_panel": False }))
		self.timer.start()

	@staticmethod
	def on_post_save(view):
		# Continue only if the current plugin settings allow this to happen.
		if MlUtils.get_sub_pref("lint", "lint_on_save"):
			view.window().run_command("ml_lint", { "show_panel": False })

	@staticmethod
	def on_load(view):
		# Continue only if the current plugin settings allow this to happen.
		if MlUtils.get_sub_pref("lint", "lint_on_load"):
			v = view.window() if int(sublime.version()) < 3000 else view
			v.run_command("ml_lint", { "show_panel": False })

	@staticmethod
	def on_selection_modified(view):
		caret_region = view.sel()[0]
		file_path = view.file_name()
		for message_region, message_text, f_path in mlErrorGlobalStore.errors:
			if (file_path == f_path and message_region.intersects(caret_region)):
				sublime.status_message(message_text)
				return
			else:
				sublime.status_message("")

class mlErrorGlobalStore:
	errors = []

	@classmethod
	def reset(self):
		self.errors = []