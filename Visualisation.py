import gobject
from gobject import GObject
import gtk
import gtk.glade

from defs import debug


class VisualisationController(GObject):
	
	__gsignals__ = {'started': (gobject.SIGNAL_RUN_FIRST, None, ()),}
	
	def __init__(self, app):
		
		GObject.__init__(self)
		
		self._app = app
		self._glade = app.glade
		self._connection = app.connection

		self._window = self._glade.get_widget('main-window')
		
		self._images = self._glade.get_widget_prefix('imageD')
		self._labels = self._glade.get_widget_prefix('labelD')
		self._compressors = self._glade.get_widget_prefix('statusKOM')
		for image in self._compressors:
			image.set_from_stock('com-uit', gtk.ICON_SIZE_DIALOG)
		
		self._connection.connect('data-arrived', self._data_arrived_cb)
	
			
	def _data_arrived_cb(self, connection):
		debug('VisualisationController: entering _data_arrived_cb')
		for item in self._labels:
			id = gtk.glade.get_widget_name(item)[len('label'):]
			data = connection.parser[id]
			item.set_text(data.raw)
		
		for item in self._images:
			name = gtk.glade.get_widget_name(item)
			id = name[len('image'):-2]
			pos = eval(name[-1])
			data = connection.parser[id]
			value = data.raw
			if value[-pos] == '1':
				item.set_from_stock(gtk.STOCK_YES, gtk.ICON_SIZE_BUTTON)
			else:
				item.set_from_stock(gtk.STOCK_NO, gtk.ICON_SIZE_BUTTON)
		
		alarm = connection.parser['DW39'].raw
		load = connection.parser['DW46'].raw
		idle = connection.parser['DW45'].raw
		motor = connection.parser['DW44'].raw
		
		for item in self._compressors:
			name = gtk.glade.get_widget_name(item)
			pos = eval(name[-1])
			if alarm[-pos] == '1':
				item.set_from_stock('com-alarm', gtk.ICON_SIZE_DIALOG)
			elif load[-pos] == '1':
				item.set_from_stock('com-vollast', gtk.ICON_SIZE_DIALOG)
			elif idle[-pos] == '1':
				item.set_from_stock('com-nullast', gtk.ICON_SIZE_DIALOG)
			elif motor[-pos] ==  '0':
				item.set_from_stock('com-uit', gtk.ICON_SIZE_DIALOG)
			else:
				#Should not reach here
				debug('VisualisationController: status compressor %d invalid' % pos)
			
		
		