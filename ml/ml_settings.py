import sublime
import os
import re
import glob

from .ml_options import MlOptions
from .roxy_options import RoxyOptions

SETTINGS_FILE = "MarkLogic.sublime-settings"

class MlSettings:
	_stored_search_paths = None
	_search_paths = None
	_sublime_options = None

	@staticmethod
	def merge_dicts(dict1, dict2):
		for key in dict2:
			value = dict2[key]
			if ((key in dict1) and isinstance(value, dict)):
				MlSettings.merge_dicts(dict1[key], value)
			else:
				dict1[key] = value

	@staticmethod
	def settings():
		if (not MlSettings._sublime_options):
			default_file = os.path.join("Packages", "MarkLogic", SETTINGS_FILE)
			user_file = os.path.join(sublime.packages_path(), "User", SETTINGS_FILE)

			default_options = MlOptions(default_file)

			MlSettings._sublime_options = default_options.options.copy()

			if (os.path.exists(user_file)):
				user_options = MlOptions(user_file)
				MlSettings.merge_dicts(MlSettings._sublime_options, user_options.options)

		return MlSettings._sublime_options

	def write_settings_sub_pref(self, key, sub_key, value):
		user_file = os.path.join(sublime.packages_path(), "User", SETTINGS_FILE)
		user_options = MlOptions(user_file)
		user_options.set_sub_pref(key, sub_key, value)

	def __init__(self):
		self._roxy_options = None
		self._proj_options = None

	def get_search_paths(self):
		stored_search_paths = self.get_xcc_pref("search_paths")

		if (not stored_search_paths):
			return None

		# make it an array
		if (not isinstance(stored_search_paths, list)):
			stored_search_paths = [stored_search_paths]

		if (stored_search_paths != MlSettings._stored_search_paths):
			MlSettings._stored_search_paths = stored_search_paths
			resolved_search_paths = []
			for search_path in stored_search_paths:
				if os.path.exists(search_path):
					resolved_search_paths.append(search_path)
				else:
					# attempt to find the paths relative to the options file
					current_options_file = self.get_current_options_file()
					if (re.match(SETTINGS_FILE, current_options_file) == None):
						root_folder = os.path.dirname(current_options_file)

						for found_path in glob.glob(os.path.join(root_folder, search_path)):
							resolved_search_paths.append(found_path)

				MlSettings._search_paths = resolved_search_paths

		return MlSettings._search_paths

	def projectOptions(self):
		if not self._proj_options:
			self._proj_options = MlOptions()
		return self._proj_options

	def roxyOptions(self):
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

		if (self.use_roxy() == True and self.roxyOptions().has_key(sub_key)):
			return self.roxyOptions().get(sub_key)

		return self.settings().get(key).get(sub_key)

	def set_sub_pref(self, key, sub_key, value):
		if self.projectOptions().has_key(key):
			self.projectOptions().set_sub_pref(key, sub_key, value)
		elif (self.use_roxy() == True and self.roxyOptions().has_key(key)):
			# do nothing for roxy
			return
		else:
			o = self.settings().get(key)
			o[sub_key] = value
			self.settings()[key] = o
			self.write_settings_sub_pref(key, sub_key, value)

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

	def get_current_options_file(self):
		options_file = self.projectOptions().options_file()
		if options_file:
			return options_file

		if (self.use_roxy()):
			options_file = self.roxyOptions().options_file()
			if options_file:
				return options_file

		return os.path.join(sublime.packages_path(), "User", SETTINGS_FILE)

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
