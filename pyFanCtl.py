#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#                                                                             #
# pyFanCtl - fan control for IBM/Lenovo laptops                               #
# Copyright (C) 2014  Alexander Böhm (alnxdr.boehm <AT> gmail.com)            #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU Affero General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU Affero General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the GNU Affero General Public License    #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

import os
import sys
import datetime

USER_ACCEPT_WARNING_FILE = '%s/.pyfanctrl' % (os.environ.get('HOME'))

try:
	import pygtk
	pygtk.require("2.0")
except:
	sys.exit(1)

try:
	import gtk
	import gtk.glade
	import gobject
	import cairo
except:
	sys.exit(1)

class FanState:
	IBM_FAN_ACPI_PATH='/proc/acpi/ibm/fan'

	def __init__(self):
		None	

	def test_maybe_functional(self):
		if os.path.isfile(FanState.IBM_FAN_ACPI_PATH):
			return True
		else:
			return False

	def get_system_data(self):
		f = open(FanState.IBM_FAN_ACPI_PATH, 'r')
		data = f.read()
		f.close()

		d = dict()

		for i in data.split('\n'):
			j = i.replace('\t', '').split(':')
			if len(j) == 2:
				if j[0] in ['level', 'speed', 'status']:
					d[j[0]] = j[1]

		return d


	def command(self, cmd_string):
		f = open(FanState.IBM_FAN_ACPI_PATH, 'w')
		data = f.write(cmd_string)
		f.close()

	def get_enabled(self):
		if self.get_system_data()['status'] == 'disabled':
			return False

		return True

	def get_level(self):
		return self.get_system_data()['level']

	def get_speed(self):
		return int(self.get_system_data()['speed'])

	def set_enabled(self, enabled=True):
		if enabled == False:
			self.command('disable')
		else:
			self.command('enable')

	def set_level(self, level):
		self.command('level %i' % level)

	def set_auto(self):
		self.command('level auto')

	def set_disengaged(self):
		self.command('level disengaged')


class ControlGui:
	def __init__(self, x, y, fan):
		self.fan = fan

		gui = gtk.glade.XML('data/gui.glade')

		self.dialog = gui.get_widget('window')
		self.radio_off = gui.get_widget('radiobutton_off')
		self.radio_auto = gui.get_widget('radiobutton_auto')
		self.radio_disengaged = gui.get_widget('radiobutton_disengaged')
		self.radio_manuel = gui.get_widget('radiobutton_manuel')
		self.scale_speed = gui.get_widget('scale_speed')
		self.label_speed = gui.get_widget('label_speed')
		self.button_about = gui.get_widget('about')
		self.button_quit = gui.get_widget('quit')

		self.update_from_system_state()

		signals = {
			'on_quit_clicked' : self.on_quit_clicked,
			'on_about_clicked' : self.on_about_clicked,
			'on_speed_format_value' : self.on_speed_format_value,
			'on_radiobutton_off_toggled' : self.on_radiobutton_off_toggled,
			'on_radiobutton_auto_toggled' : self.on_radiobutton_off_toggled,
			'on_radiobutton_disengaged_toggled' : self.on_radiobutton_off_toggled,
			'on_radiobutton_manuel_toggled' : self.on_radiobutton_off_toggled,
			'on_window_focus_out_event' : self.on_window_focus_out_event 
		}
		gui.signal_autoconnect(signals)

		self.dialog.move(x, y)
		self.dialog.show()

	def update_from_system_state(self):
		if self.fan.get_enabled():
			level = self.fan.get_level()
			if level == 'auto':
				self.radio_auto.set_active(True)
				self.scale_speed.hide()

			elif level == 'disengaged' or level == 'full-speed':
				self.radio_disengaged.set_active(True)
				self.scale_speed.hide()

			else:
				try:
					level = int(level)
					self.radio_manuel.set_active(True)
					self.scale_speed.set_value(level)
					self.scale_speed.show()

				except:
					print 'error while convering level %s to integer' % (level)

		else:
			self.radio_off.set_active(True)
			self.scale_speed.hide()

		self.label_speed.set_label('fan speed: %i' % self.fan.get_speed())

	def toogled_update_mode(self, button):
		if button == self.radio_off:
			if button.get_active():
				self.fan.set_enabled(False)

		elif button == self.radio_auto:
			if button.get_active():
				self.fan.set_auto()

		elif button == self.radio_disengaged:
			if button.get_active():
				self.fan.set_disengaged()

		elif button == self.radio_manuel:
			if button.get_active():
				self.fan.set_level(3)
				self.scale_speed.set_value(3)
				self.scale_speed.show()
			else:
				self.scale_speed.hide()

	def on_quit_clicked(self, data):
		self.fan.set_enabled()
		self.fan.set_auto()
		gtk.main_quit()

	def on_about_clicked(self, data):
		dialog = gtk.AboutDialog()
		dialog.set_name(u'pyFanCtl')
		dialog.set_program_name(u'Python fan control')
		dialog.set_version(u'0.2')
		dialog.set_comments(u'Fan control for IBM/Lenovo laptops with ibm-acpi kernel module')
		dialog.set_website(u'https://github.com/aboehm/pyfanctl')
		dialog.set_license('''pyFanCtl - fan control for IBM/Lenovo laptops
Copyright (C) 2010  Alexander Boehm

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.''')
		dialog.set_authors(['Alexander Böhm (2014)'])
		dialog.run()
		dialog.destroy()

	def on_radiobutton_off_toggled(self, radio, data=None):
		self.toogled_update_mode(radio)
	
	def on_radiobutton_auto_toggled(self, radio, data=None):
		self.toogled_update_mode(radio)

	def on_radiobutton_disengaged_toggled(self, radio, data=None):
		self.toogled_update_mode(radio)

	def on_radiobutton_manuel_toggled(self, radio, data=None):
		self.toogled_update_mode(radio)

	def on_speed_format_value(self, button, data):
		level = round( button.get_value() )
		button.set_value(level)
		self.fan.set_level(level)

	def on_window_focus_out_event(self, event, data=None):
		self.dialog.destroy()

class StatusIcon(gtk.StatusIcon):
	def __init__(self, fan):
		self.fan = fan
		gtk.StatusIcon.__init__(self)
		self.set_from_file('data/status.png')
		self.set_visible(True)
		self.connect('activate', self.on_activate)
		self.connect('popup-menu', self.on_popup_menu)

	def on_quit(self, data):
		self.fan.set_enabled()
		self.fan.set_auto()
		gtk.main_quit()

	def on_activate(self, data):
		os.spawnlpe(os.P_NOWAIT, 'fan-control', os.environ)

	def on_popup_menu(self, status, button, time):
		_, rect, _ = self.get_geometry()
		ControlGui(rect.x, rect.y, self.fan)

if __name__ == '__main__':
	fan = FanState()

	if fan.test_maybe_functional() == False:
		print 'Control interface not found. Exiting. Is thinkpad-acpi kernel module loaded?'
		sys.exit(0)

	if os.path.isfile(USER_ACCEPT_WARNING_FILE) == False:
		dlg = gtk.MessageDialog(type=gtk.MESSAGE_WARNING, message_format="This software can control your system fan. Operational errors or software failures can harm your system. This is the first and the last warning. If unsure press cancel!", buttons=gtk.BUTTONS_OK_CANCEL)
		dlg.set_title('This software can harm your computer! Continue?')
		answer = dlg.run()
		dlg.destroy()

		if int(answer) == int(gtk.RESPONSE_OK):
			f = open(USER_ACCEPT_WARNING_FILE, 'w')
			f.write('%s : user accepted warning message' % (datetime.datetime.now()))
			f.close()
		else:
			sys.exit()

	StatusIcon(fan)
	gtk.main()

