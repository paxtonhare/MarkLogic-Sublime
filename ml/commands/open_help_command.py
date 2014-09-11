import sublime, sublime_plugin
import re
import webbrowser

class OpenHelpCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		region = self.view.sel()[0]
		if (region.size() > 0):
			func = self.view.substr(region)
		else:
			func = self.view.substr(self.view.word(region))

		# clean it up a little
		func = re.sub(r"[\r\n()\[\]]", "", func)
		func = re.sub(r"\s+$", "", func)
		if (re.match(r"^[^a-zA-Z]", func)):
			func = ""
		webbrowser.open_new_tab('http://docs.marklogic.com/' + func)