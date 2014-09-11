import sublime, sublime_plugin

import webbrowser

class OpenHelpSearchCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		region = self.view.sel()[0]
		if (region.size() > 0):
			word = self.view.substr(region)
		else:
			word = self.view.substr(self.view.word(region))
		webbrowser.open_new_tab('http://developer.marklogic.com/search?q=' + word + '&p=1')