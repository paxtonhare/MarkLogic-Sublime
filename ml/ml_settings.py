import sublime
import os

from .ml_options import MlOptions
from .roxy_options import RoxyOptions

SETTINGS_FILE = "MarkLogic.sublime-settings"

class MlSettings:
	_settings = None
	_roxy_options = None
	_proj_options = None

	@staticmethod
	def settings():
		return sublime.load_settings(SETTINGS_FILE)

	def projectOptions(self):
		# return MlOptions()
		if not self._proj_options:
			self._proj_options = MlOptions()
		return self._proj_options

	def roxyOptions(self):
		# return RoxyOptions(self.roxy_env())
		if not self._roxy_options:
			self._roxy_options = RoxyOptions(self.roxy_env())
		return self._roxy_options

	def roxy_env(self):
		return MlSettings.settings().get("xcc").get("roxy_environment") or "local"

	def use_roxy(self):
		return MlSettings.settings().get("xcc").get("use_roxy_settings") == True

	def get_pref(self, key):
		if self.projectOptions().has_key(key):
			return self.projectOptions().get(key)
		elif (self.use_roxy() == True and self.roxyOptions().has_key(key)):
			return self.roxyOptions().get(key)
		return self.settings().get(key)

	def get_sub_pref(self, key, sub_key):
		if self.projectOptions().has_subkey(key, sub_key):
			return self.projectOptions().get_sub_pref(key, sub_key)

		if (self.use_roxy() == True and self.roxyOptions().has_key(key)):
			return self.roxyOptions().get(key)

		return self.settings().get(key).get(sub_key)

	def set_sub_pref(self, key, sub_key, value):
		if self.projectOptions().has_key(key):
			self.projectOptions().set_sub_pref(key, sub_key, value)
		elif (self.use_roxy() == True and self.roxyOptions().has_key(key)):
			# do nothing for roxy
			return
		else:
			o = MlUtils.settings().get(key)
			o[sub_key] = value
			MlUtils.settings().set(key, o)
			sublime.save_settings(SETTINGS_FILE)

	def get_xcc_pref(self, key):
		return self.get_sub_pref("xcc", key)

	def set_xcc_pref(self, key, value):
		self.set_sub_pref("xcc", key, value)

	def set_content_db(self, name):
		self.set_xcc_pref("content_database", name)

	def set_modules_db(self, name):
		self.set_xcc_pref("modules_database", name)

	def set_lint_on_save(self, value):
		self.set_sub_pref("lint", "lint_on_save", value)

	@staticmethod
	def debug():
		return MlSettings.settings().get("debug") == True

	@staticmethod
	def lint_scroll_to_error():
		return MlSettings.settings().get("lint").get("scroll_to_error") == True

	@staticmethod
	def lint_highlight_selected_regions():
		return MlSettings.settings().get("lint").get("highlight_selected_regions") == True

	@staticmethod
	def lint_on_edit():
		return MlSettings.settings().get("lint").get("lint_on_edit") == True

	@staticmethod
	def lint_on_edit_timeout():
		return MlSettings.settings().get("lint").get("lint_on_edit_timeout")

	@staticmethod
	def lint_on_save():
		return MlSettings.settings().get("lint").get("lint_on_save") == True

	@staticmethod
	def lint_on_load():
		return MlSettings.settings().get("lint").get("lint_on_load") == True

	@staticmethod
	def enable_marklogic_functions():
		return MlSettings.settings().get("autocomplete").get("enable_marklogic_functions") == True
