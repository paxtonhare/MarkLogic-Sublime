import sublime
import re
import os.path
import json

##
# Finds the closest .ml-sublime-options file in the hierarchy and loads it
##
class MlOptions():
	options_file = None

	def read_file_contents(self, file_name):
		with open(file_name, "r") as myfile:
			file_contents = myfile.read()
		return file_contents

	def write_file_contents(self, file_name, contents):
		with open(file_name, "w") as myfile:
			myfile.write(contents)

	def find_options_file(self):
		paths = []
		# find all the directories with options files
		for folder in sublime.active_window().folders():
			for dirname, dirnames, filenames in os.walk(folder, topdown=False):
				if '.ml-sublime-options' in filenames:
					paths.append(dirname)

		paths = sorted(paths)
		# walk up the tree until our path matches one in the above array
		current_filename = sublime.active_window().active_view().file_name()
		if current_filename:
			pwd = os.path.dirname(current_filename)
			last_dir = ''
			count = 0
			while pwd != last_dir and count < 50:
				if pwd in paths:
					return os.path.join(pwd, '.ml-sublime-options')
				last_dir = pwd
				pwd = os.path.dirname(pwd)
				count = count + 1
		elif len(paths) > 0:
			return os.path.join(paths[0], '.ml-sublime-options')

		return None

	def get_pref(self, key):
		if self.options and key in self.options:
			return self.options[key]
		return None

	def get_sub_pref(self, key, sub_key):
		if self.options:
			if key in self.options:
				if sub_key in self.options[key]:
					return self.options[key][sub_key]
		return None

	def set_sub_pref(self, key, sub_key, value):
		if self.options:
			if key in self.options:
				self.options[key][sub_key] = value
				self.write_file_contents(self.options_file, json.dumps(self.options, sort_keys=True, indent=4))

	def has_key(self, key):
		return self.options and key in self.options

	def has_subkey(self, key, sub_key):
		return self.options and key in self.options and sub_key in self.options[key]

	def __init__(self):
		self.options = None
		self.options_file = self.find_options_file()
		if self.options_file:
			self.options = json.loads(self.read_file_contents(self.options_file))
