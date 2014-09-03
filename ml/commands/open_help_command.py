import sublime, sublime_plugin

import webbrowser

class OpenHelpCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		func = self.view.substr(self.view.word(self.view.sel()[0]))
		webbrowser.open_new_tab('http://docs.marklogic.com/' + func)