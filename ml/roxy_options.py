import sublime
import re
import os.path

class RoxyOptions():
	build_props_file = None

	def merge_options(self, file_contents):
		for line in file_contents.splitlines():
			m = re.match(r"^\s*([^#=\s]+)\s*=\s*([^=\s]+)", line)
			if m:
				self.options[m.group(1)] = m.group(2)

	def read_file_contents(self, file_name):
		with open(file_name, "r") as myfile:
			file_contents = myfile.read()
		return file_contents

	def translate_key(self, key):
		keys = {
			"ml_host": "server",
			"xcc_port": "xcc-port",
			"use_https": "use-https",
			"content_database": "content-db",
			"modules_database": "modules-db",
			"user": "user",
			"password": "password"
		}
		if key in keys:
			return keys[key]
		return None

	def has_key(self, key):
		new_key = self.translate_key(key)
		return new_key and self.options and new_key in self.options

	def get(self, key):
		new_key = self.translate_key(key)
		if new_key and self.options and new_key in self.options:
			return self.options[new_key]
		return None

	def do_subs(self):
		previous_orphan_count = 0
		loop_count = 0
		while True:
			orphan_count = 0
			for k in self.options:
				v = self.options[k]
				m = re.search(r"\$\{([^}]+)\}", v)
				if m and m.group(1) in self.options:
					self.options[k] = re.sub(r"\$\{([^}]+)\}", self.options[m.group(1)], v)
				else:
					orphan_count = orphan_count + 1
			if (orphan_count == previous_orphan_count or loop_count > 10):
				break
			else:
				previous_orphan_count = orphan_count
			loop_count = loop_count + 1

	def get_deploy_dir(self):
		for folder in sublime.active_window().folders():
			path = os.path.join(folder, 'deploy')
			if (os.path.isdir(path)):
				return path
		return None

	def options_file(self):
		return self.build_props_file


	def __init__(self, env):
		self.options = {}
		settings = sublime.load_settings("MarkLogic.sublime-settings")

		deploy_dir = self.get_deploy_dir()
		if (deploy_dir):
			default_props = os.path.join(deploy_dir, "default.properties")
			build_props = os.path.join(deploy_dir, "build.properties")
			self.build_props_file = build_props

			env_props = os.path.join(deploy_dir, "%s.properties" % env)

			self.merge_options(self.read_file_contents(default_props))
			self.merge_options(self.read_file_contents(build_props))

			if os.path.isfile(env_props):
				self.merge_options(self.read_file_contents(env_props))

			self.do_subs()

			server_key = "%s-server" % env
			if server_key in self.options:
				self.options["server"] = self.options[server_key]
			else:
				raise Exception("Missing %s definition in Roxy options" % server_key)