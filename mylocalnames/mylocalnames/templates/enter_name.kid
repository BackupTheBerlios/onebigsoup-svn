<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>My Local Names (${namespace})</title>
</head>

<body>

<p class="activity_bar">
  <a href="/">My Local Names:</a>
  <a href="${namespace_url}">(${namespace})</a>:
  <b>enter a name</b>
</p>

    <p>You are naming a page!</p>

<form action="submit_name" method="post">
<input type="hidden" name="namespace" py:attrs="value=namespace" />
<input type="hidden" name="password" value="${password}" />

<table class="ui">
  <tbody>
    <tr>
      <td class="input_explain" colspan="1" rowspan="3">
        Pick a name<br/>
        for the page!</td>
      <td />
      <td class="input_title">Name:</td>
    </tr>
    <tr>
      <td class="input_prompt">&rarr;</td>
      <td><input name="name" size="33" /></td>
    </tr>
    <tr>
      <td />
    </tr>

    <tr>
      <td class="input_explain" colspan="1" rowspan="3">
        This is the page<br/>
        you are naming.
      </td>
      <td />
      <td class="input_title">URL:</td>
    </tr>
    <tr>
      <td class="input_prompt">&rarr;</td>
      <td><input size="94" name="url" value="${url}" /></td>
    </tr>
    <tr>
      <td />
    </tr>

    <tr>
      <td />
      <td />
      <td><input value="Name it!" type="submit" /></td>
    </tr>
  </tbody>
</table>

</form>

</body>
</html>
