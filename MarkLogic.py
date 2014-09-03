import sublime
import sys
import os
import locale

if int(sublime.version()) > 3000:
	st_version = 3
else:
	st_version = 2

reload_mods = []
for mod in sys.modules:
	if (mod[0:10] == 'MarkLogic.' or mod[0:3] == 'ml.' or mod == 'ml') and sys.modules[mod] != None:
		reload_mods.append(mod)

mod_prefix = ''
if st_version == 3:
	mod_prefix = 'MarkLogic.'
	from imp import reload

mods_load_order = [
	'ml.xcc',
	'ml.commands',
	'ml.commands.debug_command'
]

for suffix in mods_load_order:
	mod = mod_prefix + suffix
	if mod in reload_mods:
		reload(sys.modules[mod])

try:
	# Python 3
	from .ml.xcc import Xcc
	from .ml.commands import *
except (ValueError):
	# Python 2
	from ml.xcc import Xcc
	from ml.commands import *