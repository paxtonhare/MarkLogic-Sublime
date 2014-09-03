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

def get_sigs(filename, files):
	root = ET.parse(filename)
	for e in root.findall('.//xhtml:table', namespaces={'xhtml':"http://www.w3.org/1999/xhtml"}):
		for se in e.findall('./xhtml:tr/xhtml:td/xhtml:a[@id]', namespaces={'xhtml':"http://www.w3.org/1999/xhtml"}):
			sig = u''.join(e.itertext()).encode('utf-8').strip()
			sig = ''.join([i if ord(i) < 128 else ' ' for i in sig])
			sig = re.sub(r"\n", "", sig, re.DOTALL | re.M | re.U)
			sig = re.sub(r"\s+", " ", sig, re.DOTALL | re.M | re.U)
			sig = re.sub(r"\(\s+", "(", sig)
			sig = re.sub(r"\s+\)", ")", sig)
			sig = re.sub(r"\) as.*$", ")", sig)
			sig = re.sub(r"\[|\]", "", sig)

			desc = re.sub(r" as\s.*?(?=,|\)$)+", "", sig)
			desc = re.sub(r"^[^(]+", "", desc)
			if (desc == "()"):
				desc = None
			sig = re.sub(r"\$", make_increment_params(), sig)
			sig = re.sub(r",", "},", sig)
			sig = re.sub(r"\)$", "})", sig)

			function_name = re.match(r"([^(]+)\(", sig).group(1)

			obj = {
				"content": sig,
				"trigger": function_name
			}
			if (desc):
				obj['description'] = desc + '                                                    '

			files.append(obj)
	return files

functions = []
exclude_list = ["All.html", "REST-Resources.html", "management-rest-api.html", "packageREST.html"]
for root, dirnames, filenames in os.walk(dir):
	for filename in fnmatch.filter(filenames, '*.html'):
		if (filename not in exclude_list and re.match(r"RESTclient", filename) == None):
			get_sigs(dir + "/" + filename, functions)

with open('../marklogic_builtins/ml-functions.json', 'w') as f:
	f.write(json.dumps(functions, sort_keys=True))