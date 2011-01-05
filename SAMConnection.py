#!/usr/bin/python

import os, urllib2, socket
from urllib2 import URLError

REALM='Kaeser1'
USER='Kaeser1'
PASSWD='11'
PAGE='super/prozes.htm'

TIMEOUT = 6
MAX_TIMEOUTS = 1

from defs import debug


class SAMConnection(object):
	
	def setHost(self, host):
		self._uri = self._uri = 'http://%s/%s' % (host, PAGE)
		auth_handler = urllib2.HTTPBasicAuthHandler()
		auth_handler.add_password(REALM,
						uri=self._uri,
						user=USER,
						passwd=PASSWD)
		self._opener.add_handler(auth_handler)
		
	def getHost(self):
		return string.split(self._uri, '/')[3]

	host = property(getHost, setHost)
	
	def __init__(self, host):
		
		self._uri = 'http://%s/%s' % (host, PAGE)
		self._url = None
		
		socket.setdefaulttimeout(TIMEOUT)
		
		proxy_handler = urllib2.ProxyHandler({})
		auth_handler = urllib2.HTTPBasicAuthHandler()
		auth_handler.add_password(REALM,
								uri=self._uri,
								user=USER,
								passwd=PASSWD)
		self._opener = urllib2.build_opener(proxy_handler)
		self._opener.add_handler(auth_handler)
		
				
	def read(self):
		debug('SAMConnection: in read')
		try:
			debug('SAMConnection: trying to open %s' % self._uri)
			self._url = self._opener.open(self._uri)
			debug('SAMConnection: trying to read %s' % self._uri)
			res =  self._url.read()
			return res
		except AttributeError:
			raise SAMConnectionNotOpenError
		finally:
			self._url.close()


		
class SAMConnectionError (Exception):
	pass
	
class SAMConnectionNotOpenError (SAMConnectionError):
	pass
	
class SAMConnectionTimeoutError (SAMConnectionError):
	pass

	
	
if __name__ == '__main__':
	connection = SAMConnection('172.24.12.42')
	connection.open()
	connection.read()
	
	
	
	
	
	
	
	
	
