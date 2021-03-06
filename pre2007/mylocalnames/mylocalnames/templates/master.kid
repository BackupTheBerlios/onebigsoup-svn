<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import sitetemplate ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">

<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'">
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title py:replace="''">Your title goes here</title>
    <div py:replace="item.text"/>
    <div py:replace="item[:]"/>
    <link href="static/css/site.css" type="text/css" rel="stylesheet" />
    <script src="static/javascript/site.js" />
</head>

<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'">
    <div py:if="tg_flash" class="flash" py:content="tg_flash"></div>
    
    <div py:replace="item[:]"/>

<p class="fine_print"><a href="http://ln.taoriver.net/">Local Names</a>
is a community Open Source / Free Software
project led by <a href="http://www.speakeasy.org/%7Elion/">Lion Kimbro.</a>
Source code is available via project SVN repository.</p>

</body>
</html>