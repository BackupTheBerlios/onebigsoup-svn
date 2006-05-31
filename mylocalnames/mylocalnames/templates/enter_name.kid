<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>My Local Names - My Namespace</title>
</head>

<body>
    <p>You are naming a page in a Local Names namespace.</p>
    <p>Namespace: <a href="${namespace_url}"><b>${namespace}</b></a></p>

    <form action="submit_name" method="post">
    <input type="hidden" name="namespace" py:attrs="value=namespace" />
    <input type="hidden" name="password" value="${password}" />
    <p>name: <input name="name" size="43" /></p>
    <p>url: <input name="url" value="${url}" size="80" /></p>
    <p><input type="submit" /></p>
</form>

</body>
</html>
