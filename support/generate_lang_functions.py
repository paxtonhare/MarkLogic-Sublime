#!/bin/python
#
# builds marklogic builtins from api docs.
# point it at $dir/pubs/apidocs after unzipping the api docs

import os
import re
import json
import fnmatch
import xml.etree.ElementTree as ET

def make_increment_params(start=1):
	count = [start - 1]
	def create_increment_params(match):
		count[0] += 1
		return "${%d:\\$" % count[0]
	return create_increment_params

dir = "/path/to/MarkLogic_pubs/pubs/apidocs"

def get_funcs(filename, final_functions):
	root = ET.parse(filename)
	for e in root.findall('.//xhtml:table', namespaces={'xhtml':"http://www.w3.org/1999/xhtml"}):
		for se in e.findall('./xhtml:tr/xhtml:td/xhtml:a[@id]', namespaces={'xhtml':"http://www.w3.org/1999/xhtml"}):
			# sanitize the html into a function string
			sig = u''.join(e.itertext()).encode('utf-8').strip()
			sig = ''.join([i if ord(i) < 128 else ' ' for i in sig])
			sig = re.sub(r"\n", "", sig, re.DOTALL | re.M | re.U)
			sig = re.sub(r"\s+", " ", sig, re.DOTALL | re.M | re.U)
			sig = re.sub(r"\(\s+", "(", sig)
			sig = re.sub(r"\s+\)", ")", sig)
			sig = re.sub(r"\) as.*$", ")", sig)

			function_name = re.match(r"([^(]+)\(", sig).group(1)

			m = re.search(r"([^:]+):(.*)", function_name)

			if m:
				prefix = m.group(1)
				name = m.group(2)

			if not prefix in final_functions:
				final_functions[prefix] = {}
			group = final_functions[prefix]
			group[name] = name
	return final_functions

functions = {}

exclude_list = ["All.html", "REST-Resources.html", "management-rest-api.html", "packageREST.html"]
for root, dirnames, filenames in os.walk(dir):
	for filename in fnmatch.filter(filenames, '*.html'):
		if (filename not in exclude_list and re.match(r"RESTclient", filename) == None):
			get_funcs(dir + "/" + filename, functions)

pruned_functions = {}
for group in sorted(functions, key=lambda s: s.lower()):
	print("%s:(%s)" % (group, '|'.join(sorted(functions[group], key = lambda s: s.lower()))))