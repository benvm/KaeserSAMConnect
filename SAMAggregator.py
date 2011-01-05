
import time

from SAMParser import SAMParser
from SAMConnection import SAMConnection, SAMConnectionTimeoutError



#HOST = 'bvm.homelinux.net:8980'
HOST='172.24.12.42'
USER = 'Kaeser1'
PASSWD = '11'
INTERVAL = 10


class SAMAggregator(object):
	
	def __init__(self):
		
		self.parser = SAMParser()
		self.connection = SAMConnection(HOST)
		self.interval = INTERVAL
		
		
	def run(self):
	
		while True:
			self.connection.open()
			data = self.connection.read()
			
			self.parser.parseData(data)
			
			print 'ID      NAME                                    VALUE'
			print '-----------------------------------------------------' 
			for item in self.parser.values:
				output = '%s   %s        %s' % (item.id, item.name, item.raw)
				print output

			time.sleep(INTERVAL)
			
			
			
			
			
if __name__ == '__main__':
	agg = SAMAggregator()
	agg.run()










VALUES = [  
			'DW 64',
			'DW 58',
			'DW 98',
			'DW 66',
]
            


