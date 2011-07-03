#!/usr/bin/env python

import web
import config
from config import render
from index import Index
from arch import Arch
from profile import Profile
from mirror import Mirror
from feature import Feature
from kwd import Keyword
from use import Use
from repo import Repo
from lang import Lang
from host import Host

urls = (
	r'/', 'Index',
	r'/arch', 'Arch',
	r'/profile', 'Profile',
	r'/mirror', 'Mirror',
	r'/feature', 'Feature',
	r'/keyword', 'Keyword',
	r'/use', 'Use',
	r'/repo', 'Repo',
	r'/lang', 'Lang',
	r'/host/(.+)', 'Host'
	)

app = web.application(urls, globals())

app.notfound = config.notfound
app.internalerror = config.internalerror

if __name__ == "__main__":
  app.run()