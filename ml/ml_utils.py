import sublime
import os

SETTINGS_FILE = "MarkLogic.sublime-settings"

class MlUtils:
	@staticmethod
	def get_pref(key):
		return sublime.load_settings(SETTINGS_FILE).get(key)

	@staticmethod
	def get_sub_pref(key, sub_key):
		return sublime.load_settings(SETTINGS_FILE).get(key).get(sub_key)

	@staticmethod
	def debug():
		return MlUtils.get_pref("debug") == True

	@staticmethod
	def log(log_me):
		if (MlUtils.debug()):
			print(log_me)