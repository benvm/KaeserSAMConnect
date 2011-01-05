import os
import user
import datetime
from time import time

import gobject
from gobject import GObject
import gtk
import gtk.glade

import xlutils, xlwt, xlrd

import defs
from defs import debug


class LoggingController(GObject):
	
	def __init__(self, app):
		
		self._glade = app.glade
		
		self._workbook = None
		self._worksheet = None
		self._working = False
		self._logcount = 0
		self._sheetcount = 0
		self._overflows = 0
		
		self._dir = None
		self._file = None
		
		self._compressors = self._glade.get_widget_prefix('statusKOM')
		
		self._file_chooser = self._glade.get_widget('filechooserbutton')
		dir = os.path.join(user.home, 'CompressorLogs')
		if not os.path.exists(dir):
			os.mkdir(dir)
		self._file_chooser.set_current_folder(dir)
		
		self._log_button = self._glade.get_widget('log-button')
		self._log_button.connect('toggled', self._log_button_toggled)
		
		self._connection = app.connection
		self._connection.connect('data-arrived', self._data_arrived_cb)
		
		
	def _log_button_toggled(self, toggle):
		if toggle.get_active():
			if not self._file:
				self._dir = self._file_chooser.get_filename()
				if not self._dir or not os.access(self._dir, os.W_OK):
					dialog = gtk.MessageDialog(None, 
												gtk.DIALOG_DESTROY_WITH_PARENT,
												gtk.MESSAGE_ERROR,
												gtk.BUTTONS_OK,
												'%s is not writable' % self._dir)
					dialog.run()
					dialog.destroy()
					toggle.set_active(False)
					return
				now = datetime.datetime.today()
				d = now.date().isoformat()
				t = now.time().strftime('%H-%M-%S')
				self._filename = 'Compressors-log-%s_%s.xls' % (d, t)
				self._file = os.path.join(self._dir, self._filename)
			self._worksheet = None
			self._sheetcount += 1
			self._working = True
		else:
			self._working = False
			self._logcount = 0
			self._overflows = 0
			if self._workbook:
				self._workbook.save(self._file)
			self._worksheet = None
			
		self._file_chooser.set_sensitive(not self._working)
			
		
	def _data_arrived_cb(self, connection):
		debug('LoggingController: entering _data_arrived_cb')
		debug('LoggingController: logcount: %s,   overflows: %s' % (self._logcount, self._overflows))
		if not self._working:
			return

		if not self._workbook:
			self._workbook = xlwt.Workbook('latin1')
		if self._logcount >= defs.MAX_LOGCOUNT:
			self._overflows += 1
			self._logcount = 0
			self._worksheet = None
		if not self._worksheet:
			self._logcount = 0
			self._worksheet = self._workbook.add_sheet('Log%d-%d' % 
										(self._sheetcount, self._overflows))

			for col, item in enumerate(('datum', 'tijd', 'druk')):
				self._worksheet.write(0, col, item)
				
			for item in self._compressors:
				name = gtk.glade.get_widget_name(item)
				num = eval(name[-1])
				text = 'Compressor %d' % num
				col = num + 3
				self._worksheet.write(0, col, text)

		self._logcount += 1
		
		data = (connection.parser['DD100'].raw,
				connection.parser['DD98'].raw,
				connection.parser['DW66'].raw)

		for col, item in enumerate(data):
			self._worksheet.write(self._logcount, col, item)
					
		alarm = connection.parser['DW39'].raw
		load = connection.parser['DW46'].raw
		idle = connection.parser['DW45'].raw
		motor = connection.parser['DW44'].raw
		
		for item in self._compressors:
			name = gtk.glade.get_widget_name(item)
			pos = eval(name[-1])
			if alarm[-pos] == '1':
				text = 'ALARM'
			elif load[-pos] == '1':
				text = 'VOLLAST'
			elif idle[-pos] == '1':
				text = 'NULLAST'
			elif motor[-pos] ==  '0':
				text = 'UIT'
			else:
				#Should not reach here
				debug('LoggingController: status compressor %d invalid' % pos)
				text = 'invalid'
			self._worksheet.write(self._logcount, pos + 3, text)
				
		self._workbook.save(self._file)
			

	def activate(self, active):
		self._log_button.set_active(active)
	
		
		