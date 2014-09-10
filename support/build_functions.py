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

def break_apart_optional_params(sig):
	m = re.search(r"([^(]+)\((.+)?\)", sig)
	if m:
		function_name = m.group(1)
		if (m.group(2)):
			params = re.split(r",\s*", m.group(2))
		else:
			params = []

	required_params = []
	optional_params = []
	for param in params:
		if re.match(r"\[([^]]+)\],?", param):
			optional_params.append(re.sub(r"\[|\]", "", param))
		else:
			required_params.append(param)

	functions = []
	previous_optional_params = []

	# add the function with any required params
	functions.append("%s(%s)" % (function_name, ', '.join(required_params) ))

	for param in required_params:
		previous_optional_params.append(param)

	# add 1 function for each additional optional parameter
	for param in optional_params:
		previous_optional_params.append(param)
		functions.append("%s(%s)" % (function_name, ', '.join(previous_optional_params)))
	return functions

def get_sigs(filename, final_functions):
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

			# if there are optional params, break this thing up into multiple instances
			signatures = break_apart_optional_params(sig)
			for signature in signatures:
				desc = re.sub(r" as\s.*?(?=,|\)$)+", "", signature)
				desc = re.sub(r"^[^(]+", "", desc)
				desc = re.sub(r",\s+", ",", desc)
				if (desc == "()"):
					desc = None

				# wrap the parameters with ${n:} where n is the parameter #
				if re.search(r"\$", signature):
					signature = re.sub(r"\$", make_increment_params(), signature)
					signature = re.sub(r",", "},", signature)
					signature = re.sub(r"\)$", "})", signature)

				function_name = re.match(r"([^(]+)\(", signature).group(1)

				obj = {
					"content": signature,
					"trigger": function_name
				}
				if (desc):
					obj['description'] = desc

				final_functions[signature] = obj
	return final_functions

functions = {}

exclude_list = ["All.html", "REST-Resources.html", "management-rest-api.html", "packageREST.html"]
for root, dirnames, filenames in os.walk(dir):
	for filename in fnmatch.filter(filenames, '*.html'):
		if (filename not in exclude_list and re.match(r"RESTclient", filename) == None):
			get_sigs(dir + "/" + filename, functions)

pruned_functions = []
for k in sorted(functions):
	pruned_functions.append(functions[k])

with open('../marklogic_builtins/ml-functions.json', 'w') as f:
	f.write(json.dumps(pruned_functions, sort_keys=True))