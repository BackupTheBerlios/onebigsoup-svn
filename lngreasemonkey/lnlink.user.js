// This script will convert LocalNames from [[your local name here]] format 
// into an <a href> for every textarea on every page you visit.  You can use
// it to write LocalNames in your blog, your web-based IM client, and your 
// web-based e-mail client!
// 
// You're going to want to scroll down so you can set a couple of
// configuration settings.
// 
// If you have any questions or run into any problems, feel free to e-mail me.
// -- Jonathan Roes <jonathan.roes@gmail.com>
//
// ==UserScript==
// @name          LocalNames Link
// @namespace     http://jonathanroes.blogspot.com
// @description   Script to convert LocalNames links into <a href>'s
// @include       *
// ==/UserScript==

// Stuff you will want to change 
//----------------------------------------------------------------------

// namespace_url: the URL of your LocalNames namespace
var namespace_url = 'http://taoriver.net:9000/description?namespace=jroes';

// localname_server: the LocalNames resolving server you want to use.  you can
// probably leave this set to the default
var localname_server = 'http://ln.taoriver.net:8123/';

var lnre = /\[\[[^\]]+\]\]/g; 
var answerre = /<value><string>(.+?)<\/string><\/value>/;

if (!GM_xmlhttpRequest) {
	alert('Your Greasemonkey is out of date.  Please update it before using this script.');
} else {
	window.addEventListener('keydown', keyhandler, true);
}

function keyhandler(e) {
	if (e.which == 32 && e.target.nodeName.toLowerCase() == "textarea") { // spacebar
		var matches = e.target.value.match(lnre);
		
		if (matches) {
			for (var i = 0; i < matches.length; i++) {
				match = matches[i].replace('[[','').replace(']]','');

				GM_xmlhttpRequest({ 
					method: 'POST',
					url: localname_server,
					headers: {'User-Agent': 'Greasemonkey', 'Accept': 'application/xml,text/xml'},
					data: '<?xml version="1.0"?><methodCall><methodName>lnquery.lookup</methodName><params><param><string>'+namespace_url+'</string></param><param><string>'+matches[i]+'</string></param></params></methodCall>',
					onload: function (details) { 
							var url = details.responseText.match(answerre)[1];
							// we should be using the error code here instead
							if (url.indexOf("record not found") == -1) {
								// save our replacement text and calculate new position
								replacementtext = '<a href="'+url+'">'+match+'</a>';
								var matchre = new RegExp("\\[\\["+match+"\\]\\]", "gim");

								// if we are going to replace something past the selection...
								var matcharray = matchre.exec(e.target.value);

								if (matcharray) {
									var newposition = (e.target.selectionStart - (matcharray.index + (match.length+4))) + (matcharray.index + replacementtext.length);
								
									e.target.value = e.target.value.replace(matchre, replacementtext);
									// set the new position
									e.target.selectionStart = newposition;
									e.target.selectionEnd = newposition;
								}
							}
						}
				});
			}
		}
	}
}
