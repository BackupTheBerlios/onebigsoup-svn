<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>My Local Names (${namespace}) -- CONFIRM</title>
</head>

<body>
    <p>The URL may contain a password.</p>
    <p>Are you <b>sure</b> that you want to submit this?</p>
    <p>name: ${name}</p>
    <p>url: <b>${url}</b></p>

    <form action="submit_name" method="post">
    <input type="hidden" name="namespace" py:attrs="value=namespace" />
    <input type="hidden" name="password" value="${password}" />
    <input type="hidden" name="name" value="${name}" />
    <input type="hidden" name="url" value="${url}" />
    <p><input type="checkbox" name="confirm">Confirm: "Yes: I am OK with this URL being publicly visible."</input></p>
    <p><input type="submit" /></p>
    </form>
</body>

</html>
