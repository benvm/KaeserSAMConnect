#!/usr/bin/python


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


	def __init__(self):
		
		self.parser_data = []

		self.soup = BeautifulSoup.BeautifulSoup()

		self._categories = {}
		self._values = {}

	def parseData(self, data):

		self._categories = {}
		self._values = {}
		
		data = data.decode('latin1')
		self.soup.reset()
		self.soup.feed(data)
		self.soup.close()

		def check(tag):
			if not tag.name == 'a':
				return False
			if not tag.has_key('href'):
				return False
			if not tag['href'][:1] == '#' or tag['href'] == '#top':
				return False
			return True


		for item in self.soup.findAll(check):
			
			values = []
			rows = []
			lines = []

			catId = item.attrMap['href'][1:]
			catName = item.u.font.string.replace('&amp;', 'and')
			table = self.soup.find('a', {'name' : catId}).parent.parent.parent

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
	
				self._values[valId] = pValue
			
			pCat = ParserCategory(catId, catName, values)
			
			self._categories[catId] = pCat


	def getValue(self, valId):
		return self._values[valId]


	def getCategory(self, catId):
		return self._categories[catId]


	def __getitem__(self, key):
		return self.getValue(key)


	def has_key(self, key):
		return self._values.has_key(key)



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

	

