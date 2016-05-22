(:
 : Builds the xquery typeahead completion files. One for each version
 : 7-9
 :)
declare namespace apidoc = "http://marklogic.com/xdmp/apidoc";

import module namespace json = "http://marklogic.com/xdmp/json"
	at "/MarkLogic/json/json.xqy";

declare function local:camel-case(
	$str as xs:string) as xs:string
{
	if( fn:contains($str , "-" ) ) then
		let $subs :=  fn:tokenize($str,"-")
		return
			fn:string-join((
				$subs[1],
				for $s in $subs[ fn:position() gt 1 ]
				return (
					fn:upper-case( fn:substring($s , 1 , 1 )) , fn:lower-case(fn:substring($s,2)))),"")
	else $str
};

declare function local:get-type($param-type as xs:string, $code-type)
{
	if ($code-type = "xquery") then
		$param-type
	else
		switch ($param-type)
			case "xs:string" return
				"String"
			case "xs:boolean" return
				"Boolean"
			default return
				$param-type
};

declare function local:dump-funcs(
	$module as element(apidoc:module),
	$type as xs:string)
{
	let $functions :=
		for $func in $module/apidoc:function
		let $name :=
			let $prefix := $func/@lib
			let $local-name :=
				if ($type = "javascript") then
					local:camel-case($func/@name)
				else
					$func/@name
			let $joiner :=
				if ($type = "xquery") then ":"
				else "."
			return
				$prefix || $joiner || $local-name
		let $params := $func/apidoc:params/apidoc:param[fn:not(@class) or @class = $type]
		let $optional-count := fn:count($params[@optional = fn:true()])
		let $param-count := fn:count($params)
		let $final-params :=
			for $param in $func/apidoc:params/apidoc:param[fn:not(@class) or @class = $type]
			let $param-type := local:get-type($param/@type, $type)
			let $prefix :=
				if ($type eq "xquery") then
					"$"
				else ()
			return
				$prefix || $param/@name || " as " || $param-type
		for $i in fn:reverse(0 to $optional-count)
		let $content :=
			let $params :=
				for $p at $idx in fn:subsequence($final-params, 1, $param-count - $i)
				let $p :=
					if ($type = "xquery") then
						"\" || $p
					else
						$p
				return
					"${" || $idx || ":" || $p || "}"
			return
				$name || "(" || fn:string-join($params, ", ") || ")"
		let $trigger := $name
		let $desc as xs:string? := "(" || fn:string-join(fn:subsequence($final-params, 1, $param-count - $i), ", ") || ")"
		return
			object-node {
				"content": $content,
				"trigger": $trigger,
				"description": $desc
			}
	return
		$functions
};

declare function local:dump-em($ml-version, $dir, $output-dir)
{
	for $type in ("xquery", "javascript")
	let $uri :=
		if ($type = "xquery") then
			$output-dir || "ml-xquery-functions-" || $ml-version || ".json"
		else
			$output-dir || "ml-javascript-functions-" || $ml-version || ".json"
	let $funcs :=
		for $file as xs:string in (xdmp:filesystem-directory($dir)/dir:entry/dir:pathname)
		let $module := xdmp:document-get($file)/apidoc:module
		return
			local:dump-funcs($module, $type)
	let $array := xdmp:to-json(json:to-array($funcs))
	return
		xdmp:save($uri, document { $array }, <options xmlns="xdmp:save"><media-type>application/json</media-type></options>)
};

(:
  The directory where you have downloaded the MarkLogic_x.pub.zip files
  ex:
  let $dir-containing-pub-zips := "/Users/username/Downloads/"
:)
let $dir-containing-pub-zips :=

(:
  The directory where your sublime plugin code lives.
  ex:
    let $output-dir := "/Users/username/src/MarkLogic-Sublime/marklogic_builtins/"
:)
let $output-dir :=


for $version in (7 to 9)
let $file := "/Users/phare/Downloads/MarkLogic_" || $version || "_pubs.zip"
let $zip := xdmp:document-get($file)/binary()
for $type in ("xquery", "javascript")
let $uri :=
	if ($type = "xquery") then
		$output-dir || "ml-xquery-functions-" || $version || ".json"
	else
		$output-dir || "ml-javascript-functions-" || $version || ".json"
let $funcs :=
	for $name as xs:string in (xdmp:zip-manifest($zip)/*:part[fn:matches(., "pubs/raw/apidoc/.+\.xml")])
	let $module := xdmp:zip-get($zip, $name, <options xmlns="xdmp:zip-get"><format>xml</format></options>)/apidoc:module
	return
		local:dump-funcs($module, $type)
let $array := xdmp:to-json(json:to-array($funcs))
return
	xdmp:save($uri, document { $array }, <options xmlns="xdmp:save"><media-type>application/json</media-type></options>)
