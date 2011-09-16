# qllbot - Python powered SILC and IRC bot #
  
License: [**BSD**](http://creativecommons.org/licenses/BSD/)  
  
This bot requires [**pysilc 0.5**](http://developer.berlios.de/projects/python-silc/)
and the [**SILC Toolkit**](http://silcnet.org/software/download/toolkit/) (pysilc
dependancy) if you want to use it with SILC. IRC has no special dependancies.
Currently it just supports Python 2.6/2.7.
  
Check the [**qllbot wiki**](https://github.com/qll/qllbot/wiki) if you have any
questions or want to learn how to develop modules.  
  
Feel free to email me if you need support.

## Installation for SILC functionality ##

Note: If you just want to use the bot for IRC it will work out of the box! If
you want to use the bot in your SILC channels, follow these instructions:  
  
Warning: Due to recent changes SILC support won't work out of the box. I am working on
restoring all features, but as I switched to IRC you might experience some problems due
to a lack of testing with SILC.
  
First install the SILC Toolkit with development headers. If your distribution
includes the needed packages, install them with your packet manager. Anyways
- if you want the newest version of the toolkit or you can't get the toolkit
in a normal way (or you have problems with libiconv) you have to compile it from
source. I recommend compiling it without libiconv which caused a lot of problems
with my SILC Toolkit.  
	$ ./configure --without-iconv
	$ make
	# make install
This should install everything needed. Now you have to compile pysilc without
iconv. Just change the line <code>libraries = ['iconv', 'silc', 'silcclient'],</code>
into <code>libraries = ['silc', 'silcclient']</code> in setup.py. This caused
no problems with my installation, yet. Now build and install:  
	$ python setup.py build
	# python setup.py install
  
qllbot should work out of the box now. Just edit your settings.py and run it in
a terminal. Everything should work fine now.  
	$ python qllbot.py 

## Run as background process ##

Forking qllbot to a background process is as simple as adding the -d flag to its
parameters. Example: <code>$ python qllbot.py -d</code>. 
