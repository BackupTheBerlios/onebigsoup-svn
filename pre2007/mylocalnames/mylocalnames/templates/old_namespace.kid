<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>My Local Names - My Namespace</title>
</head>

<body>
    <h1><center><font style='background-color: black; padding: 10px' color='yellow'>-- ${namespace} --</font></center></h1>

    <p>You made it to <span py:replace="namespace">namespace</span>.</p>

<h2>Bookmarklet</h2>

<p>(give user bookmarklet)</p>

<p><a href="${bookmarklet_url}">store local name</a></p>

<h2>Namespace Description</h2>

<p>Your namespace description is at: <a href="${description_url}">${description_url}</a></p>

<h2>Browser Redirect</h2>

(tell how to redirect web browser)

<h2>Link Namespace</h2>

<form action="namespace" method="post">
    <input type="hidden" name="namespace" py:attrs="value=namespace" />
    <input type="hidden" name="password" py:attrs="value=password" />
    <p>link key: <input name="linkkey" /></p>
    <p>link url: <input name="linkurl" /></p>
    <p><input type="submit" /></p>
</form>

(give space to name link to other namespace,
 and space to give url of other namespace)

(ideally, we'd let user AJAX the order around)

<h2>Delete</h2>

<form action="namespace" method="post">
    <input type="hidden" name="namespace" py:attrs="value=namespace" checked="1" />
    <input type="hidden" name="password" py:attrs="value=password" />
    <p><input type="radio" name="deltype" value="LN">local name (LN)</input></p>
    <p><input type="radio" name="deltype" value="NS">link key (NS)</input></p>
    <p>name: <input name="delname" /></p>
    <p><input type="submit" value="delete" /></p>
</form>

<h2>Change Password</h2>

<form action="changepassword" method="post">
    <input type="hidden" name="namespace" py:attrs="value=namespace" />
    <p>old password: <input name="oldpassword" /></p>
    <p>new password: <input name="newpassword" /></p>
    <p>new password (repeat): <input name="repeat" /></p>
    <p><input type="submit" /></p>
</form>


</body>
</html>