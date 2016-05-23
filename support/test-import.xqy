xquery version "1.0-ml";

(:~
  comment here

  (: nested comment :)
:)

module (: getting crazy :) namespace blah = "http://namespace-uri";

declare option xdmp:mapping "false";

declare function blah:do-stuff(
	$x as element(blah),
	$time as xs:dateTime)
{
	()
};


declare %private function blah:a-private-function()
{
	()
};
