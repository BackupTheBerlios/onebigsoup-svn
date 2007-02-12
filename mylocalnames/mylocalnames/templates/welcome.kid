<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>My Local Names</title>
</head>

<body>

<p class="activity_bar"><b>My Local Names</b></p>

<img style="width: 383px; height: 200px;"
     alt="Name a website,... ...and refer to it in your blog!"
     src="static/images/name_and_refer.png" class="title_image" />

<form method="get" action="namespace">

<table class="ui">
  <tbody>
    <tr>
      <td class="input_explain" colspan="1" rowspan="3">
      Make up a name<br />
      for your namespace,<br />
      and type it in here!</td>
      <td />
      <td class="input_title">Namespace:</td>
    </tr>

    <tr>
      <td class="input_prompt">&rarr;</td>
      <td><input size="83" name="namespace" /></td>
    </tr>

    <tr>
      <td />
    </tr>

    <tr>
      <td class="input_explain" colspan="1" rowspan="3">
      If you like,<br />
      secure with password,<br />
      or leave blank.</td>
      <td />
      <td class="input_title">Password:</td>
    </tr>

    <tr>
      <td class="input_prompt">&rarr;</td>
      <td><input size="45" name="password" type="password" /></td>
    </tr>

    <tr>
      <td />
    </tr>

    <tr>
      <td />
      <td />
      <td><input value="Go!" type="submit" /></td>
    </tr>
  </tbody>
</table>

</form>

<center><p><a href="/all_namespaces">Root Namespace Description</a></p></center>

</body>
</html>


