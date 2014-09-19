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

from .roxy_options import RoxyOptions
from .ml_utils import MlUtils

class Xcc():

	def __init__(self):
		self.settings = {
			"ml_host": "localhost",
			"xcc_port": "8040",
			"content_database": "Documents",
			"modules_database": "Modules",
			"user": "admin",
			"password": "admin",
			"use_https": False
		}

		for setting in ["ml_host", "xcc_port", "use_https", "content_database", "modules_database", "user", "password"]:
			value = MlUtils.get_sub_pref("xcc", setting)
			if value == None:
				continue
			self.settings[setting] = value

		if (MlUtils.get_sub_pref("xcc", "use_roxy_settings") == True):
			roxy_options = RoxyOptions().options
			if "server" in roxy_options:
				self.settings["ml_host"] = roxy_options.get("server")

			if "xcc-port" in roxy_options:
				self.settings["xcc_port"] = roxy_options["xcc-port"]

			if "use_https" in roxy_options:
				self.settings["use_https"] = roxy_options["use-https"]

			if "content-db" in roxy_options:
				self.settings["content_database"] = roxy_options["content-db"]

			if "modules-db" in roxy_options:
				self.settings["modules_database"] = roxy_options["modules-db"]

			if "user" in roxy_options:
				self.settings["user"] = roxy_options["user"]

			if "password" in roxy_options:
				self.settings["password"] = roxy_options["password"]

		if MlUtils.debug():
			for k in self.settings:
				MlUtils.log("%s => %s" % (k, self.settings[k]))

		self.base_url = "http"
		if (self.settings["use_https"]):
			self.base_url = self.base_url + "s"
		self.base_url = self.base_url + "://" + self.settings["ml_host"] + ":" + self.settings["xcc_port"] + "/"

		MlUtils.log("base_url: " + self.base_url)

	def encode_params(self, params):
		if sys.version_info >= (3,):
			parse = urllib.parse
		else:
			parse = urllib

		return parse.urlencode(params)


	def http(self, url, user, password, params, headers, realm = "public"):
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

		if sys.version_info >= (3,):
			req = client.Request(url=url, headers=headers, method="POST")
		else:
			req = client.Request(url=url, headers=headers)
		return client.urlopen(req, params, 1)

	def get_header(self, response, header):
		if sys.version_info >= (3,):
			return response.getheader(header)
		else:
			return response.info().getheader(header)

	def fix_entity_refs(self, query):
		return re.sub(r"&", r"&amp;", query, re.DOTALL | re.M)

	def run_query(self, query, check=False):
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

		new_query = """
			xdmp:eval(
			  "{0}",
			  (),
			  <options xmlns="xdmp:eval">
			    <isolation>different-transaction</isolation>
			""".format(query)

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

		p = { "xquery": new_query }
		params = self.encode_params(p)
		headers = {
			"Content-type": "application/x-www-form-urlencoded",
			"Accept-Encoding": "gzip,deflate,sdch",
			"Accept": "*/*"
		}
		url = self.base_url + "eval"

		try:
			response = self.http(url, self.settings["user"], self.settings["password"], str.encode(params), headers)
			content_length = self.get_header(response, "Content-Length")
			if content_length != "0":
				content_type = self.get_header(response, "Content-Type")

				if content_type:
					boundary = re.sub("^.*boundary=(.*)$", "\\1", content_type)

				body = response.read()
				if boundary:
					# remove the last
					content = re.sub(r"\n--%s--\n$" % boundary, "", body.decode())

					# remove the first
					content = re.compile(r"^\n--%s.+?\n\n" % boundary, re.M | re.DOTALL).sub("", content)

					# split on the boundaries
					regex_str = r"\n--%s.+?\n\n" % boundary
					prog = re.compile(regex_str, re.M | re.DOTALL)

					result = "\n".join(prog.split(content))
				else:
					result = body.decode()

				MlUtils.log(result)
				return result
			else:
				return ""
		except HTTPError as e:
			return e.read().decode("utf-8")