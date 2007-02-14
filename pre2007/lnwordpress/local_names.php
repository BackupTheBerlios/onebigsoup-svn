<?php
/*
Plugin Name: Local Names
Plugin URI: http://ln.taoriver.net/wordpress.html
Description: A plugin that replaces text, when you submit content. Look under "Options" to customize.
Author: Lion Kimbro
Version: 1.0
Author URI: http://lion.taoriver.net/
*/

/*  Local Names WordPress Plugin, automatically binds names to URLs.
    Copyright (C) 2006  Lion Kimbro  (lion@speakeasy.org)

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

    Lion Kimbro (lion@speakeasy.org)
    15001 35th Ave W Apt 5-203
    Lynnwood, WA 98087-2373
*/

require_once(ABSPATH . WPINC . '/class-IXR.php');

function ln_array_to_string($array) {
	foreach ( $array as $index => $val ) {
		$val2 .= $index;
		$val2 .= ', ';
		$val2 .= $val;
		$val2 .= '; ';
	}
	return $val2;
}

function ln_array_of_arrays_to_string($aoa) {
	$ret = '[';
	foreach ( $aoa as $index => $array ) {
		$ret .= '[';
		foreach ($array as $key => $val) {
			$ret .= $val;
			$ret .= ',';
		}
	$ret .= ']';
	}
	
	$ret .= ']';
	
	return $ret;
}

// Return an array of URLs, given the results of a LNXRQueryI find_many.
// For those lookups that failed, return just: 'lookup_failed'.
function ln_process_find_many_results($results) {
	$out = array();
	foreach ( $results as $index => $error_and_string ) {
		if ( 0 == $error_and_string[0] ) {
			$out[$index] = $error_and_string[1];
		} else {
			$out[$index] = 'lookup_failed';
		}
	}

	return $out;
}

class LNStringFeeder {
	function LNStringFeeder($inStrings) {
		$this->feed = $inStrings;
	}
	function next_result() {
		return array_shift($this->feed);
	}
	function replace_w_link($matches) {
		$url = $this->next_result();
		$text = $matches[1];  // just the portion [[inside]]
		if ( isset($matches[2]) and ($matches[2] != "") )
		{
			$text = substr($matches[2], 1);  // [[link | text]]
		}
		if ( 'lookup_failed' == $url ) {
			return sprintf('<font color="red">%s</font>', $text);
		} else {
			return sprintf('<a href="%s">%s</a>', $url, $text);
		}
	}
}

function ln_ensure_options_set() {
	add_option('local_names', array('LNXRQI' => 'http://taoriver.net:8123/', 'ns_url' => 'http://ln.taoriver.net/servicenames.txt'), 'Local Names options -- LNXRQueryI, and Namespace URL');
	return get_option('local_names');
}

function ln_update_option_values($LNXRQI, $ns_url) {
	update_option('local_names', array('LNXRQI' => $LNXRQI, 'ns_url' => $ns_url));
	return get_option('local_names');
}

function ln_change_content($content) {
	$option_values = ln_ensure_options_set();
	// $pattern = '/\\[\\[([^]]+)\\]\\]/i';
        $pattern = '/\\[\\[([^\\]|]+)(|[^\\]]+)?\\]\\]/i';
	preg_match_all($pattern, $content, $out, PREG_PATTERN_ORDER);
	$matches = $out[1];  // pick the interiors, not the whole expresions
	if ( count($matches) == 0 ) {
		return $content;
	}
	foreach ( $matches as $index => $name ) {
		$matches[$index] = split(':', $name);
	}
	$client = new IXR_Client($option_values['LNXRQI']);
	if ( $client->query('lnquery.find_many', $option_values['ns_url'], $matches, 'LN', 'default') == FALSE )
	{
                $err_msg = '<p><font color="red">';
                $err_msg .= 'Hm; I can\\\'t seem to connect to the LNXRQueryI at ';
                $err_msg .= '<a href="' . $option_values['LNXRQI'] . '">' . $option_values['LNXRQI'] . '</a></font></p>';
                $err_msg .= '<p><font color="red">client-IXR.php reports: <b>' . $client->error->message . '</b></font></p>';
                return $err_msg . $content;
	}
	$results = ln_process_find_many_results($client->getResponse());
	$content = preg_replace_callback($pattern, array(new LNStringFeeder($results), 'replace_w_link'), $content);
	
	// DEBUGGING:
	// $content = $content . ln_array_to_string($results);
	
	return $content;
}

function ln_options_subpanel() {
	$option_values = ln_ensure_options_set();
	if ( isset($_POST['info_update']) ) {
		if ( isset($_POST['LNXRQI']) and isset($_POST['ns_url']) ) {
			$option_values = ln_update_option_values($_POST['LNXRQI'], $_POST['ns_url']);
			?>
                        <div class="updated">
                        <p>Local Names XML-RPC Query Interface URL set to: <b><?php _e($option_values['LNXRQI']); ?></b></p>
                        <p>Local Names namespace URL set to: <b><?php _e($option_values['ns_url']); ?></b></p>
                        </div>
                        <?php
			$client = new IXR_Client($option_values['LNXRQI']);

			if ( TRUE == $client->query('lnquery.get_server_info') ) {
				$response = $client->getResponse();
				if ( 'OBS-LNQS' == $response['IMPLEMENTATION'] ) {
					?><div class="updated"><p>Connection confirmed- You're ready to go!</p></div><?php
				} else {
					?><div class="error"><p>Hmm; I can connect to a Server, but it's not responding to lnquery.get_server_info() like I expect.</p></div><?php
				}
			} else {
				?><div class="error"><p>Cannot Connect to Name Server- <?php _e($client->error->message); ?></p></div><?php
			}
		} else {
			?>
			<div class="error"><p>ERROR: Missing either (or both) of: LNXRQI or ns_url</p></div>
			<?php
		}
	} ?>
<div class=wrap>
  <form method="post">
    <h2>Local Names Plugin</h2>
     <fieldset name="set1">
	<p><b>LNXRQueryI URL:</b> <input type="text" name="LNXRQI" size="63" value="<?php _e($option_values['LNXRQI'])?>"/></p>
        <p>"LNXRQueryI" refers to the "Query" server- a computer that takes care of figuring out what URL to bind your names to.</p>
        <p>If you don't know, see if one of these work:</p>
        <ul><li><code>http://ln.taoriver.net/lnxrqs</code></li><li><code>http://taoriver.net:8123/</code></li></ul>
        <p>That refers to two servers running on Lion's computer. They work, or at least they do today: 2006-08-25.</p>
	<p><b>Namespace URL:</b> <input type="text" name="ns_url" size="63" value="<?php _e($option_values['ns_url'])?>"/></p>
        <p>This refers to the URL of your personal namespace. (Or somebody else's namespage, that you want to make use of.)
           The namespace is what binds individual names to URLs.</p>
        <p>You could try using Lion's: <code>http://taoriver.net:9000/description?namespace=lion</code></p>
        <p>...but I think you'll have much more fun, if you get one of your own, at <a href="http://taoriver.net:9000/">My Local Names.</a></p>
     </fieldset>
<div class="submit">
  <input type="submit" name="info_update" value="<?php
	_e('Update options', 'Localization name')
	?>" /></div>
  </form>
 </div><?php
}

function ln_options_page() {
	if ( function_exists('add_options_page') ) {
		add_options_page('lnsubpaneltitle', 'Local Names', 10, basename(__FILE__), 'ln_options_subpanel');
	}
}

add_filter('content_save_pre', 'ln_change_content');
add_action('admin_menu', 'ln_options_page');

?>
