(:
 : Builds the regex strings for language functions in the
 : xquery language def file
 :)
for $type in ("fn", "xdmp", "cts")
let $names :=
	fn:distinct-values(
		for $f in xdmp:functions()
		let $name := xdmp:function-name($f)
		where fn:prefix-from-QName($name) = $type
		return
			fn:local-name-from-QName($name))
return
	$type || ":" || "(" || fn:string-join($names, "|") || ")"
