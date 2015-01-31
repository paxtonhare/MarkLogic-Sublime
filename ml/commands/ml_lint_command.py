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
from ..ml_settings import MlSettings
from ..ml_error_global_store import mlErrorGlobalStore
from .ml_event_listeners import mlEventListeners

class mlLintCommand(sublime_plugin.TextCommand):
	lint_xqy = """
		let $lint :=
			try {
				xdmp:eval('
					import module namespace test = "_PUT_MOD_NS_HERE_" at "/_ml_sublime_lint_me.xqy";
					()')
			}
			catch($ex) {$ex}
		let $clean :=
			xdmp:eval(
				'xdmp:document-delete("/_ml_sublime_lint_me.xqy")',
				(),
				<options xmlns="xdmp:eval">
					<database>{xdmp:modules-database()}</database>
				</options>)
		return
			$lint
	"""
	def run(self, edit, show_regions=True, show_panel=True):
		if False == self.file_supported():
			return

		contents = self.view.substr(sublime.Region(0, self.view.size()))
		is_module = self.is_module(contents)

		try:
			xcc = Xcc()
			query_type = "xquery"
			if MlUtils.is_server_side_js(self.view):
				query_type = "javascript"

			if is_module:
				xcc.insert_file('/_ml_sublime_lint_me.xqy', contents)
				namespace = self.get_module_ns(contents)
				contents = re.sub(r'_PUT_MOD_NS_HERE_', namespace, self.lint_xqy)

			resp = xcc.run_query(contents, query_type, not is_module)

			# reset stuff
			mlErrorGlobalStore.reset()
			mlEventListeners.reset()
			self.view.erase_regions("marklogic_compile_errors")

			if self.has_error(resp):
				description, line, column = self.error_location(resp)
				regions = []
				menuitems = []
				hint_point = self.view.text_point(line, column)
				hint_region = self.view.word(hint_point)

				status = "%d:%d %s" % (line, column, description)
				regions.append(hint_region)
				menuitems.append(status)
				mlErrorGlobalStore.errors.append((hint_region, description, self.view.file_name()))

				if show_regions:
					self.add_regions(regions)
				if show_panel:
					self.view.window().show_quick_panel(menuitems, self.on_quick_panel_selection)

				# display error on status bar
				sublime.set_timeout(functools.partial(self.updateStatus, status), 100)
		except URLError as e:
			# do this delayed becauase sublime will overwrite after a save
			status = "%s %s" % (str(e.reason), xcc.base_url)
			sublime.set_timeout(functools.partial(self.updateStatus, status), 100)
		except Exception as e:
			status = str(e)
			MlUtils.log(status)
			sublime.set_timeout(functools.partial(self.updateStatus, status), 100)

	def updateStatus(self, status):
		sublime.status_message(status)

	def file_supported(self):
		file_path = self.view.file_name()
		view_settings = self.view.settings()
		has_xqy_syntax = self.view.score_selector(self.view.sel()[0].a, 'source.xquery-ml') > 0
		has_js_syntax = MlUtils.is_server_side_js(self.view)
		return (has_xqy_syntax or has_js_syntax)

	def has_error(self, s):
		return re.search(r"\<error:error", s, re.DOTALL | re.M) != None

	def error_location(self, s):
		description = ""
		line = None
		column = None

		match = re.search(r"error:format-string\>([^<]+)\<", s, re.DOTALL | re.M)
		if match:
			description = match.group(1)

		match = re.search(r"error:frame\>(.+?)\</error:frame", s, re.DOTALL | re.M)
		if match:
			frame = match.group(1)

		if frame:
			match = re.search(r"error:line\>(\d+)\<", frame, re.DOTALL | re.M)
			if match:
				line = int(match.group(1)) - 1

			match = re.search(r"error:column\>(\d+)\<", frame, re.DOTALL | re.M)
			if match:
				column = int(match.group(1))

		if (not line or line < 0):
			line = 0

		if (not column or column < 0):
			column = 0

		return (description, line, column)

	def is_module(self, s):
		sans_comments = re.sub(r"\(:.*?:\)", "", s)
		return re.search(r"[\r\n\s]*xquery[^'\"]+(['\"])[^'\"]+?\1;?[\r\n\s]+module", sans_comments, re.DOTALL | re.M) != None

	def get_module_ns(self, contents):
		search = re.search(r"""^\s*module\s+namespace\s+[^\s]+\s*=\s*['"]([^"']+)""", contents, re.MULTILINE)
		if search != None:
			return search.groups()[0]
		return 'local'

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

		if MlSettings.lint_scroll_to_error():
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

		if not MlSettings.lint_highlight_selected_regions():
			return

		self.view.erase_regions("marklogic_lint_selected")
		self.view.add_regions("marklogic_lint_selected", [region], "meta")