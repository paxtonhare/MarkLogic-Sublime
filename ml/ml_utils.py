import sublime
import os

SETTINGS_FILE = "MarkLogic.sublime-settings"

class MlUtils:
	_settings = None

	@staticmethod
	def settings():
		if not MlUtils._settings:
			MlUtils._settings = sublime.load_settings(SETTINGS_FILE)

		return MlUtils._settings

	@staticmethod
	def get_pref(key):
		return MlUtils.settings().get(key)

	@staticmethod
	def get_sub_pref(key, sub_key):
		return MlUtils.settings().get(key).get(sub_key)

	@staticmethod
	def debug():
		return MlUtils.get_pref("debug") == True

	@staticmethod
	def log(log_me):
		if (MlUtils.debug()):
			print(log_me)

	@staticmethod
	def load_resource(name):
		if hasattr(sublime, 'load_resource'):
			return sublime.load_resource(name)
		else:
			with open(os.path.join(sublime.packages_path(), name[9:])) as f:
				return f.read()

	@staticmethod
	def set_content_db(name):
		xcc = MlUtils.settings().get('xcc')
		xcc['content_database'] = name
		MlUtils.settings().set('xcc', xcc)
		sublime.save_settings(SETTINGS_FILE)

	@staticmethod
	def set_modules_db(name):
		xcc = MlUtils.settings().get('xcc')
		xcc['modules_database'] = name
		MlUtils.settings().set('xcc', xcc)
		sublime.save_settings(SETTINGS_FILE)

	@staticmethod
	def set_lint_on_save(value):
		lint = MlUtils.settings().get('lint')
		lint['lint_on_save'] = value
		MlUtils.settings().set('lint', lint)
		sublime.save_settings(SETTINGS_FILE)