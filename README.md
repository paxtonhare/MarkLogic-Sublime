# MarkLogic Sublime Plugin

## About

A feature packed MarkLogic XQuery package for Sublime Text.

### Features:
* MarkLogic xquery extensions support "1.0-ml"
* Syntax highlighting for MarkLogic builtins
* [**Code completion**](#code-completion) for MarkLogic builtin functions
* [**XQuery Lint**](#xquery-lint) - Checks your XQuery files for errors
* [**Run on server**](#run-on-server) - Runs your XQuery file on a MarkLogic server
* [**Open MarkLogic api docs**](#open-marklogic-api-docs) for the function under the cursor
* [**Search MarkLogic online docs**](#search-marklogic-api-docs) for the word under the cursor
* [**Tab snippets**](#tab-snippets) to streamline common patterns

#### Code completion
This feature is enabled by default. Simply start typing the name of a MarkLogic function and press tab to complete. The complete function along with parameter list will be inserted in your code.
Pressing the tab key will allow you to move between the different parameters.

#### XQuery Lint
This feature performs a syntax check on your XQuery code by running it on a MarkLogic server with the static-check option enabled.
You can configure this Lint to run on load, save, and edit. _Edit check only works on Sublime Text 3_.

The lint settings are in the MarkLogic.sublime-settings file:

```
// LINT settings
"lint": {
	// Automatically lint on edit (Sublime Text 3 only).
	"lint_on_edit": false,

	// Configurable duration before re-linting.
	"lint_on_edit_timeout": 1,

	// Automatically lint when a file is loaded.
	"lint_on_load": false,

	// Automatically lint when a file is saved.
	"lint_on_save": false,

	// Highlight errors when selected.
	"highlight_selected_regions": true,

	// scroll to reveal any errors found
	"scroll_to_error": false
}
```

##### Configuring which MarkLogic server to talk to

###### Via Settings
You can specify the MarkLogic server via the MarkLogic.sublime-settings file.

###### Via Roxy
Alternatively, if you are using the [Roxy Deployer](https://github.com/marklogic/roxy) the server settings will automatically be read from your Roxy configuration files.

```
// settings for Xcc connection
"xcc": {

	// Use Settings from Roxy's properties files
	// If this is not a Roxy project then the setttings above will be used
	"use_roxy_settings": true,

	// The roxy environment configuration to use
	// Valid choices are usually [local, dev, prod] but may vary
	"roxy_environment": "local",

	// MarkLogic hostname
	"ml_host": "localhost",

	// Xcc port to communicate with for running queries
	"xcc_port": "8041",

	// The content database to use when evaluating queries
	"content_database": "Documents",

	// The modules database to use when evaluating queries
	"modules_database": "Modules",

	// user name to use when authenticating to xcc
	"user": "admin",

	// password name to use when authenticating to xcc
	"password": "admin",

	// Whether or not to use https when communicating with Xcc
	"use_https": false
},
```

#### Run On Server
Run the current file on a MarkLogic server via the "MarkLogic: Run File" command or by pressing Ctrl+Alt+r.

#### Open MarkLogic api docs
You can easily open a browser window to the documentation for a MarkLogic function.

When text is selected or your cursor is on a function name in code press the correct key combo for your platform:

* Mac: `Command + '`
* Linux: `Ctrl + '`
* Windows: `Ctrl + '`

#### Search MarkLogic online docs
You can easily search the MarkLogic online documentation for the current selection or word under the cursor.

When text is selected or your cursor is on a word press the correct key combo for your platform:

* Mac: `Command + Shift + '`
* Linux: `Ctrl + Shift + '`
* Windows: `Ctrl + Shift + '`

#### Tab Snippets
Tab Snippets will help you write code faster. Activate them by typing the trigger followed by tab.

##### Trigger: attribute
Inserts a constructed attribute
```xquery
attribute name() { () }
```
##### Trigger: element
Inserts an inline constructed element
```xquery
element name() { () }
```
##### Trigger: element
Inserts a constructed element
```xquery
element name() {
	()
}
```
##### Trigger: fun
Inserts a function declaration with the correct namespace prefix already filled out
```xquery
declare function local:name()
{
	(: code goes here :)
};
```
##### Trigger: if
Inserts an if then else statement
```xquery
if (expression) then
	()
else
	()
```
##### Trigger: ns
Inserts a namespace declaration
```xquery
declare namespace ns = "http://namespace-uri";
```
##### Trigger: switch
Inserts a switch statement _(xquery 3.0)_
```xquery
switch (expression)
	case expression return
		expression
	default return
		expression
```
##### Trigger: type
Inserts a typeswitch statement
```xquery
typeswitch(expression)
	case expression return
		expression
	default return
		expression
```
##### Trigger: variable
Inserts a variable declaration
```xquery
declare variable $x := ();
```
##### Trigger: log
Inserts a stubbed xdmp:log() call
```xquery
xdmp:log()
```
##### xqdoc
Inserts a stubbed [xqdoc](http://xqdoc.org/) comment

Press `Ctrl + Alt + d`

```xquery
(:~
 : Function description
 :
 : @param $function-param - description of param
 : @return - description of return
 :)
```

## Install Manually with Git:
Make sure you follow the instructions for the correct version of Sublime.

### Instructions for Sublime Text 3

#### Mac
	> git clone https://github.com/paxtonhare/MarkLogic-Sublime.git ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/MarkLogic

#### Linux
	> git clone https://github.com/paxtonhare/MarkLogic-Sublime.git ~/.config/sublime-text-3/Packages/MarkLogic

#### Windows
	> git clone https://github.com/paxtonhare/MarkLogic-Sublime.git "%APPDATA%/Sublime Text 3/Packages/MarkLogic"

### Instructions for Sublime Text 2

#### Mac
	> git clone https://github.com/paxtonhare/MarkLogic-Sublime.git ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/MarkLogic

#### Linux
	> git clone https://github.com/paxtonhare/MarkLogic-Sublime.git ~/.config/sublime-text-2/Packages/MarkLogic

#### Windows
	> git clone https://github.com/paxtonhare/MarkLogic-Sublime.git "%APPDATA%/Sublime Text 2/Packages/MarkLogic"
