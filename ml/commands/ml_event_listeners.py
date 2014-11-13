import sublime
import sublime_plugin

from ..ml_utils import MlUtils
from ..ml_settings import MlSettings
from ..ml_error_global_store import mlErrorGlobalStore

class mlEventListeners(sublime_plugin.EventListener):
	timer = None

	@classmethod
	def reset(self):
		# Invalidate any previously set timer.
		if self.timer != None:
			self.timer.cancel()
			self.timer = None

	@staticmethod
	def file_supported(view):
		file_path = view.file_name()
		view_settings = view.settings()
		has_xqy_syntax = view.score_selector(view.sel()[0].a, 'source.xquery-ml') > 0
		has_js_syntax = MlUtils.is_server_side_js(view)
		return (has_xqy_syntax or has_js_syntax)

	@classmethod
	def on_modified(self, view):
		# Continue only if the plugin settings allow this to happen.
		# This is only available in Sublime 3.
		if int(sublime.version()) < 3000:
			return
		if not (mlEventListeners.file_supported(view) and MlSettings.lint_on_edit()):
			return

		# Re-run the ml_lint command after a second of inactivity after the view
		# has been modified, to avoid regions getting out of sync with the actual
		# previously linted source code.
		self.reset()

		timeout = MlSettings.lint_on_edit_timeout()
		self.timer = Timer(timeout, lambda: view.window().run_command("ml_lint", { "show_panel": False }))
		self.timer.start()

	@staticmethod
	def on_post_save(view):
		# Continue only if the current plugin settings allow this to happen.
		if (mlEventListeners.file_supported(view)):
			if(MlSettings.lint_on_save()):
				view.window().run_command("ml_lint", { "show_panel": False })

	@staticmethod
	def on_load(view):
		# Continue only if the current plugin settings allow this to happen.
		if mlEventListeners.file_supported(view) and MlSettings.lint_on_load():
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