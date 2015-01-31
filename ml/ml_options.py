import sublime
import re
import os.path
import json
import glob

##
# Finds the closest .ml-sublime-options file in the hierarchy and loads it
##
class MlOptions():
	__cached_options_file = None

	def read_file_contents(self, file_name):
		with open(file_name, "r") as myfile:
			file_contents = myfile.read()
		return file_contents

	def write_file_contents(self, file_name, contents):
		with open(file_name, "w") as myfile:
			myfile.write(contents)

	def find_options_file(self):
		# walk up the tree until our path matches one in the above array
		current_filename = sublime.active_window().active_view().file_name()
		if current_filename:
			pwd = os.path.dirname(current_filename)
			last_dir = ''
			count = 0
			while pwd != last_dir and count < 50:
				test_path = os.path.join(pwd, '.ml-sublime-options')
				if os.path.exists(test_path):
					return test_path
				last_dir = pwd
				pwd = os.path.dirname(pwd)
				count = count + 1
		else:
			paths = []

			# find all the directories with options files
			for folder in sublime.active_window().folders():
				for dirname, dirnames, filenames in os.walk(folder, topdown=True):
					if '.ml-sublime-options' in filenames:
						paths.append(dirname)

			paths = sorted(paths)
			if len(paths) > 0:
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
				self.write_file_contents(self._options_file, json.dumps(self.options, sort_keys=True, indent=4))

	def has_key(self, key):
		return self.options and key in self.options

	def has_subkey(self, key, sub_key):
		return self.options and key in self.options and sub_key in self.options[key]

	def options_file(self):
		return self._options_file

	def __init__(self, options_file = None):
		self.options = None

		if options_file:
			self._options_file = options_file
		elif (MlOptions.__cached_options_file and os.path.exists(MlOptions.__cached_options_file)):
			self._options_file = MlOptions.__cached_options_file
		else:
			self._options_file = self.find_options_file()
			MlOptions.__cached_options_file = self._options_file

		if self._options_file:
			content = self.read_file_contents(self._options_file)

			# remove any comments
			# taken from http://www.lifl.fr/~riquetd/parse-a-json-file-with-comments.html
			comment_re = re.compile('(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?', re.DOTALL | re.MULTILINE)
			match = comment_re.search(content)
			while match:
				# single line comment
				content = content[:match.start()] + content[match.end():]
				match = comment_re.search(content)

			try:
				self.options = json.loads(content)
			except ValueError as e:
				print("Invalid Json Options file: %s" % self._options_file)
