xquery version "1.0-ml";

module namespace blah = "http://namespace-uri";

declare option xdmp:mapping "false";

declare function blah:do-stuff(
	$x as element(blah),
	$time as xs:dateTime)
{
	(: Tab here to start coding :)
};


declare %private function blah:a-private-function()
{
	(: Tab here to start coding :)
};
