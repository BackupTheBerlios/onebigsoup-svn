<?php
/*
Plugin Name: Lookup LocalNames
Version: 0.2
Plugin URI: http://blog.mookitty.co.uk/devblog/
Description: Add LocalName funcationality to your blog!<br /><a href="../wp-content/plugins/lookup-local-names.php?action=setoptions-lookup-local-names">Options</a>&nbsp;|&nbsp;<a href="../wp-content/plugins/lookup-local-names.php?action=install-lookup-local-names">Install</a>&nbsp;|&nbsp;<a href="../wp-content/plugins/lookup-local-names.php?action=uninstall-lookup-local-names">Uninstall</a><br>(c) 2004, licensed under the GPL
Author: Kitten
Author URI: http://blog.mookitty.co.uk

---------------------------------------------------------------------
Description:

---------------------------------------------------------------------
Quick Start:

---------------------------------------------------------------------
Detailed Instructions:

---------------------------------------------------------------------
Notes:

---------------------------------------------------------------------
Changelog:
1.0 - Intial release

---------------------------------------------------------------------
Dependancies:

notes: ([A-Z]{1,}[a-z]{2,}+[A-Z]{1,}[a-z]{2,}+[A-Z]*[a-z]{2,}*)
Good Luck!

*/
/***************-------------  SET OPTIONS SECTION  -------------***************/
if( $_GET[action] == 'setoptions-lookup-local-names' && (strpos( $_SERVER['HTTP_REFERER'], '/wp-admin/plugins.php' ) || strpos( $_SERVER['HTTP_REFERER'], 'lookup-local-names.php' ) )) {

	require('../../wp-config.php');
	$options = new lln_options_mgr( $wpdb );
	$options->update_opts($_POST);
	$options->show_form();
	echo '<p /><a href="../../wp-admin/plugins.php">Return to plugins page</a>';
	exit;
}	// End options selector

/***************-------------  END OPTIONS SECTION  -------------***************/

/***************--------------  INSTALLER SECTION  --------------***************/

if( ($_GET[action] == 'uninstall-lookup-local-names' || $_GET[action] == 'install-lookup-local-names') && strpos( $_SERVER['HTTP_REFERER'], '/wp-admin/plugins.php' ) ) {

	if( $_GET[action] == 'install-lookup-local-names' ) {
		require('../../wp-config.php');
		$install = new lln_install_mgr();
		$install->install_options();
	}	// End installer

	if( $_GET[action] == 'uninstall-lookup-local-names' ) {
		require('../../wp-config.php');
		$uninstall = new lln_install_mgr( $wpdb );
		$uninstall->uninstall_options();
	}	// End uninstaller
	echo '<p /><a href="../../wp-admin/plugins.php">Return to plugins page</a>';
	exit;
}	// End installer selector

/***************------------  END INSTALLER SECTION  ------------***************/

/***************--------------  STANDALONE SECTION  -------------***************/
/***************------------  END STANDALONE SECTION  -----------***************/

/***************---------------  PLUGIN FUNCTIONS  --------------***************/

function lookup_local_names( $post_text ) {
	require_once('Inutio-XML-RPC-lib.php');

	$server    = get_settings('mookitty_lookup-local-names_opt_server');
	$namespace = get_settings('mookitty_lookup-local-names_opt_namespace');
	$result = array();
	$pattern = "/(\[\[(.+)\]\])|(\s|!|#)([A-Z]{1,2}[a-z]+[A-Z]{1,2}[a-z]+[A-Z]*[a-z]*)(\b)/mU";
	preg_match_all( $pattern, $post_text, $result );

	for( $i=0; $i < count($result[2]); $i++ ) {
		if( !empty($result[2][$i]) ) {
			$result[4][$i] = $result[2][$i];
		}
	}
//echo '<pre>'; die(print_r($result));
	$words_to_nuke = array();
	for( $i=0; $i < count( $result[0] ); $i++) {
		unset( $exclaim );
		$exclaim = strpos($result[0][$i], "#");

		if( $exclaim !== FALSE ) {
			$words_to_nuke[] = $result[4][$i];
		}
	}
//	echo '<pre>';
//	die(print_r($words_to_nuke));

	for( $i=0; $i < count( $result[0] ); $i++) {
		unset( $delim );
		$delim = strpos($result[0][$i], "!");

		if( $delim !== FALSE ) {
			unset( $result[4][$i] );
		}
	}

	foreach ( $result[4] as $item ) {
		$lookup_list[] = $item;
	}
	if( count($result[2]) > 0 ) {
		$client = new IXR_Client($server);
		if (!$client->query('locate_list', $namespace, $lookup_list, 1)) {
			die('An error occurred - '.$client->getErrorCode().":".$client->getErrorMessage());
		}
//echo '<pre>'; print_r($lookup_list); die(print_r($client->getResponse()));

		foreach( $client->getResponse() as $local_name => $ln_uri ) {
			/**/
			if( !empty($words_to_nuke) ) {
				foreach( $words_to_nuke as $bad_word ) {
//				echo $bad_word;
					if( $local_name == $bad_word ) {
						$local_name_display = strtolower($local_name);
						break;
					} else {
						$local_name_display = $local_name;
					}
				}
			} else {
				$local_name_display = $local_name;
			}
			
			$post_text = preg_replace( "/([^\/\S]|<p>|<strong>|<code>|<em>|<ln>)(\[\[)?(#?)($local_name)(]]|\b)/mU", "$1<a href=\"$ln_uri\">$local_name_display</a>", $post_text );
		}
		$post_text = preg_replace( "/(!)([\w]+)(\s)/m", "$2", $post_text );
	}
	return $post_text;
}	// End lookup_local_names

/***************-------------- END PLUGIN FUNCTIONS  ----------*****************/

/***************---------------- GLOBAL FUNCTIONS  --------------***************/

function mk_nuke_camelcase( $item, $key ) {

}

/***************-------------- END GLOBAL FUNCTIONS  ------------***************/

/***************--------------  CLASS DEFINITIONS  --------------***************/

class lln_options_mgr {
	var $optdb;

	function lln_options_mgr( $db_handle = '' ) {
	// Let's construct
		$this->optdb = $db_handle;
	}	// End option_mgr constructor

	function update_opts( $form_val ) {
		if( count($form_val) > 0 ) {
			echo "Updating";
			$updated = FALSE;
			$server    = get_settings('mookitty_lookup-local-names_opt_server');
			$namespace = get_settings('mookitty_lookup-local-names_opt_namespace');
			if( $_POST['ln-server'] != $server ) {
				update_option('mookitty_lookup-local-names_opt_server', $_POST['ln-server'] );
			echo "...server updated";
			$updated = TRUE;
			}
			if( $_POST['ln-namespace'] != $namespace ) {
				update_option('mookitty_lookup-local-names_opt_namespace', $_POST['ln-namespace'] );
			echo "...namespace updated";
			$updated = TRUE;
			}
			if( $updated ) {
				echo "...All done!";
			} else {
				echo "...no changes made.";
			}
		}
	}	// End function update_options

	function show_form() {
		?>
		<form action="" name="options_form" method="post">
		<table>
			<thead>
				<tr>
				<th colspan="2">Edit your settings:</th>
				</tr>
			</thead>
			<tbody>
				<tr>
				<td>LocalName Server:</td>
				<td><input type="text" name="ln-server" value="<?php echo get_settings('mookitty_lookup-local-names_opt_server') ?>" size="40" maxlength="200" /></td>
				</tr>
				<tr>
				<td>LocalName NameSpace:</td>
				<td><input type="text" name="ln-namespace" value="<?php echo get_settings('mookitty_lookup-local-names_opt_namespace') ?>" size="40" maxlength="200" /></td>
				</tr>
				<tr>
				<td>&nbsp;</td>
				<td><input type="submit" name="submit" value="Update Options" /></td>
				</tr>
			</tbody>
		</table>
		</form>
		<?php
	}

}	// End class option_mgr

class lln_install_mgr {
	var $instdb;

	function lln_install_mgr( $db_handle = '' ) {
		$this->instdb = $db_handle;
	}	// End option_mgr constructor

	function install_options() {
	// Let's construct
		echo "Installing...<br />";
		if( get_settings('mookitty_lookup-local-names_opt_installed') != 'true' ) {
			add_option('mookitty_lookup-local-names_opt_installed', 'true');
			add_option('mookitty_lookup-local-names_opt_server', 'Add your server here' );
			add_option('mookitty_lookup-local-names_opt_namespace', get_settings('siteurl').'/namespace.txt' );
			echo "OK!<br />Options installed, please set your server URI using the 'options' link.<br />Use the uninstaller to remove.";
		} else {
			echo "Already installed!";
		}

	}	// End function install_options

	function uninstall_options() {
		global $tableoptions;

		echo "Uninstalling...<br />";
		$this->instdb->get_results("DELETE FROM $tableoptions WHERE option_name LIKE 'mookitty_lookup-local-names_opt_%'");
		if( $this->instdb->show_errors && $this->instdb->rows_affected > 0 ) {
	 		echo "Uninstalled.<br />";
	 	} else {
	 		echo "There was a problem uninstalling.";
	 	}
	}
}	// End class option_mgr

/***************------------  END CLASS DEFINITIONS  ------------***************/

/***************---------------  PLUGIN API HOOKS  --------------***************/
/*
add_action('', '')
*/
add_filter('the_content', 'lookup_local_names');

?>
