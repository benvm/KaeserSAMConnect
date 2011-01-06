from time import time
from threading import Thread

import gobject
import gtk
import gtk.glade

from gobject import GObject

import SAMConnection
from SAMConnection import SAMConnection, URLError
import SAMParser
from SAMParser import SAMParser

import defs
from defs import debug, error


class ConnectionController(GObject):

	__gsignals__ = {'data-arrived': (gobject.SIGNAL_RUN_FIRST, None, ()),}

	def __init__(self, app):
		GObject.__init__(self)

		self._app = app
		self._glade = app.glade
		self.parser = SAMParser()
		
		self._timeout_id = None
			
		self._interval_spin = self._glade.get_widget('interval-spinbutton')
		self._interval_spin.set_range(defs.MIN_INTERVAL, defs.MAX_INTERVAL)
		self._interval_spin.set_value(defs.INTERVAL)
		self._interval_spin.connect('value-changed', self._interval_spin_changed)
		self._timeout = self._interval_spin.get_value_as_int()
				
		self._connect_button = self._glade.get_widget('connect-button')
		
		self._host_entry = self._glade.get_widget('server-entry')
		self._host_entry.set_text(defs.HOST)
		self._host_entry.connect('changed', self._host_entry_changed)
		self._host_entry.connect('activate', lambda a: self._connect_button.set_active(True))
		
		check = self._glade.get_widget('keep-trying-check')
		self._stop_on_error = not check.get_active()
		check.connect('toggled', self._keep_trying_toggled)
		
		self._connection = SAMConnection(self._host_entry.get_text())
										
		self._connect_button.connect('toggled', self._connect_button_toggled)
		

	def _interval_spin_changed(self, spinbutton):
		self._timeout = spinbutton.get_value_as_int()
		if self._timeout_id:
			gobject.source_remove(self._timeout_id)
			self._timeout_id = gobject.timeout_add_seconds(self._timeout, self._timeout_cb)


	def _keep_trying_toggled(self, toggle):
		self._stop_on_error = not toggle.get_active()
		

	def _connect_button_toggled(self, button):
		if self._timeout_id:
				gobject.source_remove(self._timeout_id)
				self._timeout_id = None
		if button.get_active():
			try:
				data = self._connection.read()
			except URLError:
				dialog = gtk.MessageDialog(None, 
											gtk.DIALOG_DESTROY_WITH_PARENT,
											gtk.MESSAGE_ERROR,
											gtk.BUTTONS_OK,
											'Kan geen verbinding met de server maken')
				dialog.run()
				dialog.destroy()
				self._connect_button.set_active(False)
			else:
				self._timeout_id = gobject.timeout_add_seconds(self._timeout, self._timeout_cb)
				self._timeout_cb()
		
		self._host_entry.set_sensitive(not button.get_active())


	def _host_entry_changed(self, entry):
		self._connection.host = entry.get_text()


	def _timeout_cb(self):
		debug('ConnectionController: entering timeout_cb')
		th = ReadThread(self._connection)
		th.start()
		gtk.main_iteration()
		th.join()
		if th.error:
			if self._stop_on_error:
				error('ConnectionController: could not read the connection')
				dialog = gtk.MessageDialog(None, 
											gtk.DIALOG_DESTROY_WITH_PARENT,
											gtk.MESSAGE_ERROR,
											gtk.BUTTONS_OK,
											'Kan geen verbinding met de server maken')
				dialog.run()
				dialog.destroy()
				self._connect_button.set_active(False)
				return False
			else:
				return True
		else:
			data = th.data
			start = time()
			debug('ConnectionController: start parsing the data')
			self.parser.parseData(data)
			self.emit('data-arrived')
			return True	


	def activate(self, active):
		self._connect_button.set_active(active)
		
		
	
class ReadThread(Thread):
	
	def __init__(self, connection):
		Thread.__init__(self)
		self._connection = connection
		self.data = None
		self.error = False
		

	def run(self):
		try:
			start = time()
			self.data = self._connection.read()
		except URLError:
			self.error = True
			return

