"""Setup Local Names Library."""

from distutils.core import setup


setup(name="localnames",
      version='1.0',
      description='Local Names Library',
      author='Lion Kimbro',
      author_email='lion@speakeasy.org',
      url='http://purl.net/net/localnames/',
      py_modules=["lnparser", "localnames", "lncore", "webcache"])

