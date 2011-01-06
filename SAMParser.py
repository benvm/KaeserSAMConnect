#!/usr/bin/python
from threading import Thread

import BeautifulSoup


class SAMParser(object):

	@property
	def values(self):
		return self._values.values()

	@property
	def valueIds(self):
		return self._values.keys()

	@property
	def categories(self):
		return self._categories.values()

	@property
	def categoryIds(self):
		return self._categories.keys()

	@property
	def parsing(self):
		return self._parsing


	def __init__(self):
		
		self._parsing = False

		self._categories = {}
		self._values = {}

	def parseData(self, data):
		
		self._parsing = True

		th = ParseThread(data)
		th.start()
		th.join()
		self._categories = th.categories
		self._values = th.values

		self._parsing = False


	def getValue(self, valId):
		return self._values[valId]


	def getCategory(self, catId):
		return self._categories[catId]


	def __getitem__(self, key):
		return self.getValue(key)


	def has_key(self, key):
		return self._values.has_key(key)


class ParseThread(Thread):
	
	def __init__(self, data):
		Thread.__init__(self)

		self.categories = {}
		self.values = {}
		data = data.decode('latin1')
		self._soup = BeautifulSoup.BeautifulSoup()
		self._soup.reset()
		self._soup.feed(data)
		self._soup.close()		


	def run(self):

		def check(tag):
			if not tag.name == 'a':
				return False
			if not tag.has_key('href'):
				return False
			if not tag['href'][:1] == '#' or tag['href'] == '#top':
				return False
			return True


		for item in self._soup.findAll(check):
			
			values = []
			rows = []
			lines = []

			catId = item.attrMap['href'][1:]
			catName = item.u.font.string.replace('&amp;', 'and')
			table = self._soup.find('a', {'name' : catId}).parent.parent.parent

			for child in table.findChildren('tr'):
				rows.append(child)

			for row in rows[1:]:
				lines = row.findChildren('td')[-3:]
				valId = lines[0].string.replace(' ', '')
				valName = lines[1].string 
				value = lines[2].string
				if value:
					value = value.replace('&nbsp;', ' ')
				else:
					#not a string
					pass
				
				pValue = ParserValue(valId, valName, value)

				values.append(value)
	
				self.values[valId] = pValue
			
			pCat = ParserCategory(catId, catName, values)
			
			self.categories[catId] = pCat



class ParserCategory():
	def __init__(self, catId, name, values):
		self.id = catId
		self.name = name
		self.values = values


class ParserValue():
	def __init__(self, valId, name, value):
		self.id = valId
		self.name = name
		self.raw = value
		try:
			value = eval(value.replace(' ', ''))
		except (SyntaxError, AttributeError):
			pass
		finally:
			self.value = value


if __name__ == "__main__":
	f = open('../Prozessabbild.htm')
	data = f.read()
	p = SAMParser()
	p.parseData(data)
	for val in p.values:
		print p[val.id].value

	

