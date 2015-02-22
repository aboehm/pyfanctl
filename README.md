# pyfanctl

Control IBM/Lenovo thinkpad fan speed under linux with acpi

## Warning

This software can harm your system! Your fan could be affected by rapid wear
or your CPU can overheat. Don't use this software, if you don't know what you
do or ask advanced users!

## Requirements

Hardware:

* any IBM or Lenovo Laptop, that supports handling the system fan over
  thinkpad-acpi driver under Linux

Software:

* Linux based system
* Python v2
* Python GTK 2.0 libraries

## Usage

Before usage, you have to enable the fan control interface for thinkpad-acpi
module. Unload the module:

	rmmod thinkpad-acpi

Set new default options for the module by place this text into
/etc/modprobe.d/thinkpad-fan.conf file:

	options thinkpad-acpi fan_control=1

Reload the module by

	modprobe thinkpad-acpi

After this you can control the fan speed by now.

Go to the location of pyfanctl. Start the programm with superuser right by

	sudo ./pyFanCtl

alternative you can set the correct rights on /proc/acpi/ibm/fan, when you know
what are you do.

After the startup you will see a fan icon in the tray list. Right click on it
to show the control menu. There are four different modes:

* Off        - totaly turn off the fan
* Automatic  - it's the default behavior
* Disengaged - speed up the fan to maximum speed
* Manual     - set a static speed with level 0 to 7

If you shutdown the program, the fan speed will be automatic reset to Automatic
mode.

## License

This software is licensed under AGPL v3.

