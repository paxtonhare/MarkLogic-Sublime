(: Builds the regex for recognizing ML functions in the tmLanguage file :)
for $ns in ('fn', 'xdmp', 'cts')
return
	fn:string-join(
		for $x in fn:distinct-values(
			for $f in (xdmp:functions())
			let $name := xdmp:function-name($f)
			let $prefix := fn:prefix-from-QName($name)
			where $prefix = $ns
			return
			  fn:string(fn:local-name-from-QName($name)))
		order by $x ascending
		return
			$x,
		"|"
	)