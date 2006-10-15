<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>My Local Names (${namespace})</title>
</head>

<body>
  <p class="activity_bar">
  <b>Local Names:</b> <a href="/">Edit Namespace</a>
    <b>(${namespace})</b>
    &mdash; <a href="wrap.html">Wrap Wiki</a>
    &mdash; <a href="help.html">Help</a>
  </p>

  <h2>Welcome!</h2>

  <p>You've just created a Local Names namespace!</p>

  <p>A namespace is a collection of names of pages.</p>

  <p>You can <a href="${description_url}">see the source code for your namespace,</a> to get a feel for the information kept within it.</p>

  <p>Now, we're going to set you up, so that you can:</p>

  <ul>
  <li>Name pages as you find them on the Internet.</li>
  <li>Jump to those pages, by name alone.</li>
  <li>Automatically link to those pages, in your <a href="http://wordpress.org/">WordPress</a> blog.</li>
  </ul>

  <h3 class="toggled" onclick="toggle_display('name')">Name Pages!</h3>
  <div id="name">

    <p>To name pages, you need to install a bookmarklet.
       A bookmarklet is a bookmark, but with a tiny program inside.</p>

    <p>This is the bookmarklet:</p>

    <blockquote>
      <p><span class="bookmarklet"><a href="${bookmarklet_url}">Name this Page</a></span>
        &larr; Drag&nbsp; this link to your bookmarks
        toolbar.</p>
    </blockquote>

    <p>Once you've installed the bookmarklet, try it out-
       click on it, from the bookmarks toolbar.</p>

    <p>It should ask you to name this page;
       I recommend naming this page "edit."</p>

    <p>Visit some other pages on the Internet, and then push the
       "Name this page" bookmarklet.</p>

    <p>You are naming pages!</p>
  </div>

  <h3 class="toggled" onclick="toggle_display('jump')">Jump to Pages!</h3>
  <div id="jump">

    <p>This trick works in Firefox. This makes it so that you can
       jump straight to any web page, by name. Directions for Explorer may
       come
       later.</p>

    <ol>
      <li>Under "Bookmarks," choose "Manage Bookmarks."</li>
      <li>In the folder tree, open up "Bookmarks", and then select
          "Quick Searches."</li>
      <li>Click on the "New Bookmark" button.</li>
      <li>For Name, enter: <code>Local Names Lookup</code></li>
      <li>For Location, copy in: <code>http://ln.taoriver.net/redirect?namespace=${website_prefix}${description_url}&amp;path=%s</code></li>
      <li>For Keyword, enter: <code>ln</code></li>
      <li>For &nbsp;Description, enter: <code>Jump to the
          page by the given name.</code></li>
      <li>Click on "OK."</li>
      <li>Close the Bookmarks Manager.</li>
    </ol>

    <p>That's it! Try it out!</p>

    <ol>
      <li>Hold down the Alt key, and type the letter "d."
          (<code>Alt-d</code>.)
          You can release the Alt key now.</li>
      <li>The URL of the page you are at should now be highlighted,
          with a dark background.</li>
      <li>Type <code>ln edit</code>, and then Enter.</li>
      <li>You should find yourself... ...back at this page! Whoah-
           Amazing!</li>
    </ol>

    <p>To really get the effect for this one, you'll want to
    jump to a page <i>other</i> than the one you're already
    looking at.</p>

    <p>In place of "edit," put the name of a different page that
    you've already named.</p>
  </div>

  <h3 class="toggled" onclick="toggle_display('blog')">Automate Linking in your Blog!</h3>
  <div id="blog">

    <p>There is a <a href="http://ln.taoriver.net/wordpress.html">Plugin for WordPress!</a></p>

    <p>With this plugin, you can form links by your Local Names, rather than URL.</p>
  </div>

  <h2>Additional Functionality</h2>

  <p>You've seen the basics. These are other things you can do as well!
     Explore at your leisure.</p>


  <h3 class="toggled" onclick="toggle_display('link')">Link Namespace</h3>
  <div id="link" style="display:none">

    <form action="namespace" method="post">
    <input name="namespace" py:attrs="value=namespace" type="hidden" />
    <input name="password" py:attrs="value=password" type="hidden" />
    <table class="ui">
      <tbody>
      <tr>
        <td class="input_explain" colspan="1" rowspan="3">
          Make up a name<br />
          for the target namespace,
        </td>
        <td> </td>
        <td class="input_title">Link key:</td>
      </tr>

      <tr>
        <td class="input_prompt">&rarr;</td>
        <td><input size="25" name="linkkey" /></td>
      </tr>

      <tr>

        <td> </td>

      </tr>

      <tr>

        <td class="input_explain" colspan="1" rowspan="3">Enter the URL<br />

of the target<br />

namespace description.</td>

        <td> </td>

        <td class="input_title">Link URL:</td>

      </tr>

      <tr>

        <td class="input_prompt">&rarr;</td>

        <td><input size="83" name="linkurl" /></td>

      </tr>

      <tr>

        <td> </td>

      </tr>

      <tr>

        <td> </td>

        <td></td>

        <td><input value="Go!" type="submit" /></td>

      </tr>

    </tbody>
  </table>

</form>

</div>

  <h3 class="toggled" onclick="toggle_display('delete')">Delete an Entry</h3>
  <div id="delete" style="display:none">

    <p>Delete an entry from your namespace.</p>

    <form action="namespace" method="post">
    <input name="namespace" py:attrs="value=namespace" checked="1" type="hidden" />
    <input name="password" py:attrs="value=password" type="hidden" />

    <table class="ui">
    <tbody>
      <tr>
        <td class="input_explain" colspan="1" rowspan="3">Enter the name you<br />
          want to delete<br />
          from your namespace.
        </td>
        <td> </td>
        <td class="input_title">Name:</td>
      </tr>

      <tr>
        <td class="input_prompt">&rarr;</td>
        <td><input size="25" name="delname" /></td>
      </tr>

      <tr>
        <td> </td>
      </tr>

      <tr>
        <td class="input_explain" colspan="1" rowspan="3">
          In most cases, just "local name."<br />
          But if you're deleting a link to<br />
          another namespace, choose "link key."</td>
        <td> </td>
        <td class="input_title">Type:</td>
      </tr>

      <tr>
        <td class="input_prompt">&rarr;</td>
        <td>
          <p>
          <input name="deltype" value="LN" type="radio"
                 checked="checked">
          local name (LN)</input>
          </p>
          <p>
          <input name="deltype" value="NS" type="radio">
          link key (NS)</input>
          </p>
        </td>
      </tr>

      <tr>
        <td> </td>
      </tr>

      <tr>
        <td> </td>
        <td></td>
        <td><input value="delete" type="submit" /></td>
      </tr>

    </tbody>
    </table>
    </form>
  </div>

<h3 class="toggled" onclick="toggle_display('pw')">Change Password</h3>
<div id="pw" style="display:none">

<form action="changepassword" method="post">
  <input name="namespace" py:attrs="value=namespace" type="hidden" />
  <p>old password: <input name="oldpassword" /></p>

  <p>new password: <input name="newpassword" /></p>

  <p>new password (repeat): <input name="repeat" /></p>

  <p><input type="submit" /></p>

</form>

</div>

<p>Your namespace description is at: <a href="${description_url}">${description_url}</a></p>

<p class="fine_print"><a href="http://ln.taoriver.net/">Local
Names</a> is a
community Open Source / Free Software
project started by <a href="http://www.speakeasy.org/%7Elion/">Lion
Kimbro.</a>
Source code is available via project SVN repository.</p>

</body>
</html>
