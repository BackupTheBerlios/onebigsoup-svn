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

var startswithbracketsre = /^\[\[/;
var lnre = /\[\[(.+?)\]\]/;
var answerre = /<value><string>(.+?)<\/string><\/value>/;

var lastword = "";
var allTextareas;
var namespace_url = 'http://taoriver.net:9000/description?namespace=jroes';

if (!GM_xmlhttpRequest) {
    alert('Your Greasemonkey is out of date.  Please update it before using this script.');
} else {
    allTextareas = document.getElementsByTagName('textarea');
    for (var i = 0; i < allTextareas.length; i++) {
	allTextareas[i].addEventListener('keypress', keyhandler, true);
    }
}

function keyhandler(e) {
	if ( (e.which == 32) && (lastword.length > 0) ) { // spacebar
		if (lnre.exec(lastword)) {
			var oldword = lastword.replace('[[','').replace(']]','');
			GM_xmlhttpRequest({ 
				method: 'POST',
				url: 'http://ln.taoriver.net:8123/',
				headers: {'User-Agent': 'Greasemonkey', 'Accept': 'application/xml,text/xml'},
				data: '<?xml version="1.0"?><methodCall><methodName>lnquery.lookup</methodName><params><param><string>'+namespace_url+'</string></param><param><string>'+lastword+'</string></param></params></methodCall>',
				onload: function (details) { 
						var url = details.responseText.match(answerre)[1];
//						alert('url for '+oldword+': ' + details.responseText);
						e.target.value = e.target.value.replace(new RegExp("\\[\\["+oldword+"\\]\\]", "gim"), '<a href="'+url+'">'+oldword+'</a>');
					}
			});

			lastword = "";
		} else {
			if (!startswithbracketsre.exec(lastword)) {
				lastword = "";
			} else {
				lastword += " ";
			}
		}
	} else {
		lastword += String.fromCharCode(e.which);
	}
}
