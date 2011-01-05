#!/usr/bin/python


import os, urllib2


class SAMConnection(object):

	page = property(getPage, setPage)

	def getPage(self):
		return self._page


	def setPage(self, page):
		self._url = None
		self._page = page

	
	def __init__(self, host, user, passwd):
		
		self.host = host
		self.username = user
		self.passwd = passwd
		self._page = None

		self._url = None

		self._opener = None

		auth_handler = urllib2.HTTPBasicAuthHandler()
		auth_handler.add_password(realm='Kaeser Password',
                          		uri='http://' + self.host + '/',
                          		user=self.user,
                          		passwd=self.passwd)
		self._opener = urllib2.build_opener(auth_handler)


	def open(self):
		
		url = 'http://' + self.host + '/' + self.page

		self._url = self._opener.open(url)


	def read(self):
		try:
			return self._url.read()
		except AttributeError, e:
			raise SAMConnectionNotOpenError




		class SAMConnectionError (Exception)
class SAMConnectionNotOpenError (SAMConnectionError)	

