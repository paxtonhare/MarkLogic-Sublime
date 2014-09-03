(: xquery file to test xquery syntax :)
(: comment :)

declare default function namespace "http://www.w3.org/2005/xpath-functions";

declare function local:name()
{
	(: code goes here :)
};

declare function
local:name2()
{
	(: code goes here :)
};

declare function

local:name2_5()
{
	(: code goes here :)
};

declare
function
local:name3()
{
	(: code goes here :)
};

declare
function
local:name35	()
{
	(: code goes here :)
};

declare
function
local:name36

()
{
	(: code goes here :)
};


declare

function


local:name4()
{
	(: code goes here :)
};


declare %private function local:name5() {
	()
};

declare %blah function local:name6() {
	()
};

declare %java:method("java.lang.StrictMath.copySign") function local:name7($magnitude, $sign)
{

};