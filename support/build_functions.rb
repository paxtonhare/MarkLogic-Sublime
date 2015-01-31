#!/bin/ruby

require 'typhoeus'
require 'nokogiri'
require 'json'

# HTTP_ROOT = "http://docs-ea.marklogic.com"
HTTP_ROOT = "http://pubs.marklogic.com:8011"

def break_apart_optional_params(sig, is_js)
	function_name = nil
	params = nil
	sig.gsub /([^(]+)\((.+)?\)/ do |m|
		function_name = $1
		if $2
			params = $2.split(/,\s*/)
		else
			params = [] unless $2
		end
	end

	required_params = []
	optional_params = []
	params.each do |param|

		param.gsub! /-([a-z])/ do |m|
			x = $1
			x.upcase
		end if is_js

		if param.match(/\[([^\]]+)\],?/)
			optional_params.push(param.gsub(/\[|\]/, ""))
		else
			required_params.push(param)
		end
	end

	functions = []
	previous_optional_params = []

	# add the function with any required params
	functions.push("#{function_name}(#{required_params.join(', ')})")

	required_params.each do |param|
		previous_optional_params.push(param)
	end

	# add 1 function for each additional optional parameter
	optional_params.each do |param|
		previous_optional_params.push(param)
		functions.push("#{function_name}(#{previous_optional_params.join(', ')})")
	end
	return functions
end

def get_function(hydra, url, final_functions, is_js = false)
	r = Typhoeus::Request.new("#{HTTP_ROOT}#{url}", method: :get)

	r.on_complete do |response|
		if response.code.to_i == 200
			desc = nil
			html = Nokogiri::XML::Document.parse(response.body)
			html.remove_namespaces!
			html.xpath('//div[@class="pjax_enabled"]/pre[1]').each do |e|
				sig = e.inner_text
				sig = sig.gsub(/\n/, "")
				sig = sig.gsub(/\s+/, " ")
				sig = sig.gsub(/\(\s+/, "(")
				sig = sig.gsub(/\s+\)/, ")")

				sig = sig.gsub(/\)\s+as\s+[^,]+$/, ")")

				# if there are optional params, break this thing up into multiple instances
				break_apart_optional_params(sig, is_js).each do | signature|
					desc = signature.gsub(/ as\s.*?(?=,|\)$)+/, "")
					desc = desc.gsub(/^[^(]+/, "")
					desc = desc.gsub(/,\s+/, ",")
					desc = nil if (desc == "()")

					# wrap the parameters with ${n:} where n is the parameter #
					if signature.match(/\$/)
						signature = signature.gsub(/\$/).with_index do |m, i|
							if is_js
								"${#{i+1}:"
							else
								"${#{i+1}:\\$"
							end
						end
						signature = signature.gsub(/,/, "},")
						signature = signature.gsub(/\)$/, "})")
					end

					function_name = $1 if signature =~ /([^(]+)\(/

					obj = {
						"content" => signature,
						"trigger" => function_name
					}

					obj['description'] = desc if (desc)

					final_functions[signature] = obj
				end
			end
		end
	end

	hydra.queue r
end

def build_functions(url, filename, is_js = false)
	functions = {}

	hydra = Typhoeus::Hydra.new
	response = Typhoeus::Request.post(url)
	html = Nokogiri::XML::Document.parse(response.body)
	html.remove_namespaces!
	html.xpath('//table[@class="api_table"]//tr/td/a/@href').each do |link|
		get_function(hydra, link.text, functions, is_js)
	end
	hydra.run

	# hydra = Typhoeus::Hydra.new
	# if (is_js)
	# 	get_function(hydra, "/8.0/xdmp.function-signature", functions, is_js)
	# else
	# 	get_function(hydra, "/8.0/xdmp:invoke-function", functions, is_js)
	# 	get_function(hydra, "/8.0/xdmp:set-response-code", functions, is_js)
	# 	get_function(hydra, "/8.0/xdmp:function-signature", functions, is_js)
	# end

	hydra.run

	pruned_functions = []
	functions.each_value do |v|
		pruned_functions.push(v)
	end

	print(pruned_functions)
	json = JSON.generate(pruned_functions.sort_by { |o| o['content'] })
	File.open(filename, "w") { |file| file.write(json) }
end

build_functions("#{HTTP_ROOT}/8.0/all", '../marklogic_builtins/ml-xquery-functions.json')
build_functions("#{HTTP_ROOT}/8.0/js/all", '../marklogic_builtins/ml-javascript-functions.json', true)