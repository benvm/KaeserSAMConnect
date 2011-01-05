import os
from optparse import OptionParser

import gobject
from gobject import GObject
import gtk
import gtk.glade

import defs

from Visualisation import VisualisationController
from ConnectionController import ConnectionController
from LoggingController import LoggingController


class SAMConnectApp:
	def __init__(self):
		
		self._dir = os.path.dirname(__file__)
		file = os.path.join(self._dir, 'SAMView.glade')
		
		self.glade = gtk.glade.XML(file)
		
		self.window = self.glade.get_widget('main-window')
		self.window.connect('delete-event', self._on_window_delete_event)
		
		self._register_iconsets()
		
		self.connection = ConnectionController(self)
		self.visual = VisualisationController(self)
		self.logger = LoggingController(self)
		
		menu = gtk.Menu()
		menu_item = gtk.ImageMenuItem(gtk.STOCK_QUIT)
		menu_item.connect('activate', self._on_quit_menu_item_activate)
		menu.append(menu_item)
		
		self.status_icon = gtk.StatusIcon()
		self.status_icon.set_from_stock('com-vollast')
		self.status_icon.set_visible(True)
		self.status_icon.connect('activate', self._status_icon_activated)
		self.status_icon.connect('popup-menu', self._popup_menu_cb, menu)

						
	def _register_iconsets(self):
		icon_info =[('com-uit', 'com-uit.png'),
					('com-alarm', 'com-alarm.png'),
					('com-nullast', 'com-nullast.png'),
					('com-vollast', 'com-vollast.png')]
					
		iconfactory = gtk.IconFactory()
		stock_ids = gtk.stock_list_ids()
		for stock_id, file in icon_info:
			if stock_id not in stock_ids:
				pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(self._dir, file))
				iconset = gtk.IconSet(pixbuf)
				iconfactory.add(stock_id, iconset)
		iconfactory.add_default()

	
	def _status_icon_activated(self, icon):
		if self.window.get_property('visible'):
			self.window.hide()
		else:
			self.window.show_all()
	
	
	def _popup_menu_cb(self, staus_icon, button, time, menu):
		if button == 3:
			if menu:
				menu.show_all()
				menu.popup(None, None, None, 3, time)
				
		
	def _on_window_delete_event(self, window, event):
		window.hide()
		return True

	
	def _on_quit_menu_item_activate(self, item):
		self._quit_app()
		
	
	def _quit_app(self):
		self.status_icon.set_visible(False)
		self.logger.activate(False)
		self.connection.activate(False)
		gtk.main_quit()
		
		
def main():
	usage = "usage: %prog [options]"
	parser = OptionParser(usage)
	parser.set_defaults(server=defs.HOST, interval=defs.INTERVAL,
						invisible=False, connect=False, log=False,
						maxlog=defs.MAX_LOGCOUNT)
	parser.add_option('-i', '--invisible',
						action='store_true', dest='invisible')
	parser.add_option('-s', '--server', dest='server',
						help='De server waarmee verbonden moet worden')
	parser.add_option('-c', '--auto-connect',
						action='store_true', dest='connect',
						help='Maak onmiddellijk verbinding')
	parser.add_option('-l', '--auto-log',
						action='store_true', dest='log',
						help='Begin onmiddellijk te loggen')
	parser.add_option('-I', '--interval', type='int', dest='interval',
						help='Het update interval in seconden min: %s  max: %s' 
								% (defs.MIN_INTERVAL, defs.MAX_INTERVAL))
	parser.add_option('-m', '--max-log', dest='maxlog',
						help='Maximum aantal loglijnen per blad')
						
	(options, args) = parser.parse_args()
	if len(args) != 0:
		parser.error("incorrect number of arguments")
		
	defs.HOST = options.server	
	if options.interval < defs.MIN_INTERVAL:
		options.interval = defs.MIN_INTERVAL
	if options.interval > defs.MAX_INTERVAL:
		options.interval = defs.MAX_INTERVAL
	defs.INTERVAL = options.interval
	defs.MAX_LOGCOUNT = options.maxlog

	app = SAMConnectApp()
	if not options.invisible:
		app.window.show_all()	
	#activate controllers only after main loop is started 
	gobject.timeout_add_seconds(2, _activate_controllers, app, options)
	
	gtk.main()


def _activate_controllers(app, options):
	app.logger.activate(options.log)
	app.connection.activate(options.connect)
	return False


if __name__ == '__main__':
	main()
	
	
	

	