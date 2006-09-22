// A quick (well, I was up until about 8am writing it, but... any NORMAL 
// person would have done this quickly ;]) script to convert LocalNames 
// in a [[my local name here]] format into an <a href> for your blog,
// or whatever textareas you have.
// 
// -- Jonathan Roes <jonathan.roes@gmail.com>
//
// --------------------------------------------------------------------
//
// This is a Greasemonkey user script.  To install it, you need
// Greasemonkey 0.3 or later: http://greasemonkey.mozdev.org/
// Then restart Firefox and revisit this script.
// Under Tools, there will be a new menu item to "Install User Script".
// Accept the default configuration and install.
//
// To uninstall, go to Tools/Manage User Scripts,
// select "LocalNames Link", and click Uninstall.
//
// --------------------------------------------------------------------
//
// ==UserScript==
// @name          LocalNames Link
// @namespace     http://jonathanroes.blogspot.com
// @description   Script to convert LocalNames links into <a href>'s
// @include       *
// ==/UserScript==

var lnre = /\[\[[^\]]+\]\]/g; // a much better regex, courtesy of Woosta@freenode##javascript
var answerre = /<value><string>(.+?)<\/string><\/value>/;

var lastword = "";
var allTextareas;
var namespace_url = 'http://taoriver.net:9000/description?namespace=jroes';

if (!GM_xmlhttpRequest) {
    alert('Your Greasemonkey is out of date.  Please update it before using this script.');
} else {
    allTextareas = document.getElementsByTagName('textarea');
    for (var i = 0; i < allTextareas.length; i++) {
	allTextareas[i].addEventListener('keydown', keyhandler, true);
    }
}

function keyhandler(e) {
	if (e.which == 32) { // spacebar
		var matches = e.target.value.match(lnre);
		
		for (var i = 0; i < matches.length; i++) {
			match = matches[i].replace('[[',"").replace(']]',"");

			GM_xmlhttpRequest({ 
				method: 'POST',
				url: 'http://ln.taoriver.net:8123/',
				headers: {'User-Agent': 'Greasemonkey', 'Accept': 'application/xml,text/xml'},
				data: '<?xml version="1.0"?><methodCall><methodName>lnquery.lookup</methodName><params><param><string>'+namespace_url+'</string></param><param><string>'+matches[i]+'</string></param></params></methodCall>',
				onload: function (details) { 
						var url = details.responseText.match(answerre)[1];
//						alert('url for '+oldword+': ' + details.responseText);
						e.target.value = e.target.value.replace(new RegExp("\\[\\["+match+"\\]\\]", "gim"), '<a href="'+url+'">'+match+'</a>');
					}
			});
		}
	}
}
