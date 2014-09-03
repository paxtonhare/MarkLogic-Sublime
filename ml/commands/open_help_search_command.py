import sublime, sublime_plugin

import webbrowser

class OpenHelpSearchCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		word = self.view.substr(self.view.word(self.view.sel()[0]))
		webbrowser.open_new_tab('http://developer.marklogic.com/search?q=' + word + '&p=1')