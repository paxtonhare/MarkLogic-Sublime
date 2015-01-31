import sys
import re

if sys.version_info >= (3,):
	import http.client
	import urllib.parse
	import urllib.request
	from urllib.error import HTTPError
else:
	import httplib
	import urllib
	import urllib2
	from urllib2 import HTTPError

import socket

from .ml_utils import MlUtils
from .ml_settings import MlSettings

class Xcc():

	def __init__(self):
		self.settings = {
			"ml_host": "localhost",
			"xcc_port": "8040",
			"content_database": "Documents",
			"modules_database": "Modules",
			"user": "admin",
			"password": "admin",
			"timeout": "1",
			"use_https": False
		}

		mlSettings = MlSettings()
		for setting in ["ml_host", "xcc_port", "use_https", "content_database", "modules_database", "user", "password", "timeout", "output_options"]:
			value = mlSettings.get_xcc_pref(setting)
			if value == None:
				continue
			self.settings[setting] = value

		if MlSettings.debug():
			for k in self.settings:
				MlUtils.log("%s => %s" % (k, self.settings[k]))

		self.base_url = "http"
		if (self.settings["use_https"] == True):
			self.base_url = self.base_url + "s"
		self.base_url = self.base_url + "://" + self.settings["ml_host"] + ":" + self.settings["xcc_port"] + "/"

		MlUtils.log("base_url: " + self.base_url)

	def encode_params(self, params):
		if sys.version_info >= (3,):
			parse = urllib.parse
		else:
			parse = urllib

		return parse.urlencode(params)


	def http(self, url, user, password, params, verb, headers, realm = "public"):
		# configure the timeout for htttp
		timeout = float(self.settings['timeout'])
		socket.setdefaulttimeout(timeout)

		if sys.version_info >= (3,):
			client = urllib.request
		else:
			client = urllib2

		passwdmngr = client.HTTPPasswordMgrWithDefaultRealm()
		passwdmngr.add_password(realm, url, user, password)
		digest_authhandler = client.HTTPDigestAuthHandler(passwdmngr)
		basic_authhandler = client.HTTPBasicAuthHandler(passwdmngr)
		opener = client.build_opener(basic_authhandler, digest_authhandler)

		client.install_opener(opener)

		if (verb == "PUT" and self.is_string(params)):
			params = params.encode('utf-8')

		if sys.version_info >= (3,):
			req = client.Request(url=url, headers=headers, method=verb, data=params)
		else:
			req = client.Request(url=url, headers=headers, data=params)
			req.get_method = lambda: verb

		return client.urlopen(req)

	def is_string(self, input):
		if sys.version_info >= (3,):
			return isinstance(input, str)
		else:
			return isinstance(input, basestring)

	def get_header(self, response, header):
		if sys.version_info >= (3,):
			return response.getheader(header)
		else:
			return response.info().getheader(header)

	def fix_entity_refs(self, query):
		return '&amp;'.join(query.split('&'))

	def run_query(self, query, query_type="xquery", check=False):
		if ("content_database" in self.settings):
			content_db = self.settings["content_database"]
		else:
			content_db = None

		if ("modules_database" in self.settings):
			modules_db = self.settings["modules_database"]
		else:
			modules_db = None

		query = self.fix_entity_refs(query)
		query = query.replace('"', '""')

		eval_func = "xdmp:eval"
		if query_type == "javascript":
			eval_func = "xdmp:javascript-eval"

		new_query = """
			%s(
			  "%s",
			  (),
			  <options xmlns="xdmp:eval">
			    <isolation>different-transaction</isolation>
			""" % (eval_func, query)#.format(query, eval_func)

		if (content_db != None):
			new_query = new_query + '<database>{{xdmp:database("{0}")}}</database>'.format(content_db)

		if (modules_db != None):
			new_query = new_query + '<modules>{{xdmp:database("{0}")}}</modules>'.format(modules_db)

		if (check == True):
			new_query = new_query + '<static-check>true</static-check>'

		new_query = new_query + """
			  </options>)
		"""

		if (check == True):
			new_query = "try {" + new_query + "} catch($ex) { $ex[error:code != ('XDMP-MODNOTFOUND')] }"

		output_options = ""
		if "output_options" in self.settings:
			for option in self.settings["output_options"]:
				output_options = """%sdeclare option xdmp:output "%s";\n""" % (output_options, option)

		new_query = output_options + new_query

		p = { "xquery": new_query }
		params = self.encode_params(p)
		headers = {
			"Content-type": "application/x-www-form-urlencoded",
			"Accept-Encoding": "gzip,deflate,sdch",
			"Accept": "*/*"
		}
		url = self.base_url + "eval"
		MlUtils.log("url: " + url)
		try:
			response = self.http(url, self.settings["user"], self.settings["password"], str.encode(params), "POST", headers)
			MlUtils.log(response)
			content_length = self.get_header(response, "Content-Length")
			if content_length != "0":
				content_type = self.get_header(response, "Content-Type")

				if content_type:
					boundary = re.sub("^.*boundary=(.*)$", "\\1", content_type)

				body = response.read()
				if boundary:
					# remove the last
					content = re.sub(r"[\r\n]+--%s--[\r\n]+$" % boundary, "", body.decode())

					# remove the first
					content = re.compile(r"^[\r\n]+--%s.+?[\r\n]+" % boundary, re.M | re.DOTALL).sub("", content)

					# split on the boundaries
					regex_str = r"[\r\n]+--%s.+?[\r\n]+" % boundary
					prog = re.compile(regex_str, re.M | re.DOTALL)

					parts = []

					partSplitter = re.compile(r"[\r\n][\r\n]", re.M | re.DOTALL)
					for part in prog.split(content):
						splits = partSplitter.split(part)
						parts.append(splits[len(splits) - 1])

					result = "\n\n".join(parts)
				else:
					result = body.decode()

				MlUtils.log(result)
				return result
			else:
				return ""
		except HTTPError as e:
			raise Exception(e.read().decode("utf-8"))

	def insert_file(self, uri, file_contents):
		if ("modules_database" in self.settings):
			modules_db = self.settings["modules_database"]
		else:
			raise Exception('No modules database configured')

		params = {}
		params["uri"] = uri
		params["format"] = "text"
		params["dbname"] = modules_db

		headers = {
			'Content-Type': "text/xml",
			'Accept': "text/html, text/xml, image/gif, image/jpeg, application/vnd.marklogic.sequence, application/vnd.marklogic.document, */*"
		}

		url = self.base_url + "insert?" + self.encode_params(params)
		try:
			response = self.http(url, self.settings["user"], self.settings["password"], file_contents, "PUT", headers)
		except HTTPError as e:
			return e.read().decode("utf-8")