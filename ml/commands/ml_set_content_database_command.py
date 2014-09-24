import sublime, sublime_plugin

from ..xcc import Xcc
from ..ml_utils import MlUtils

class mlSetContentDatabaseCommand(sublime_plugin.WindowCommand):
	def run(self):
		xcc = Xcc()
		resp = xcc.run_query("""
			fn:string-join(xdmp:databases() ! xdmp:database-name(.), ",")
		""")
		self.dbs = resp.split(',')
		self.window.show_quick_panel(self.dbs, self.on_done)

	def on_done(self, picked):
		MlUtils.set_content_db(self.dbs[picked])
