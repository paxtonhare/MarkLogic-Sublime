import sublime, sublime_plugin

from ..xcc import Xcc
from ..ml_settings import MlSettings

class mlSetModulesDatabaseCommand(sublime_plugin.WindowCommand):
	def run(self):
		try:
			xcc = Xcc()
			resp = xcc.run_query("""
				fn:string-join(xdmp:databases() ! xdmp:database-name(.), ",")
			""")
			self.dbs = resp.split(',')
			self.window.show_quick_panel(self.dbs, self.on_done)
		except Exception as e:
			print("Error getting Database List:")
			print(e)
			self.window.show_quick_panel(["Error getting list. See console (ctrl+`)"], None)

	def on_done(self, picked):
		if (picked >= 0):
			MlSettings().set_modules_db(self.dbs[picked])
