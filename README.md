# qllbot - Python powered SILC bot #
  
License: [**BSD**](http://creativecommons.org/licenses/BSD/)  
  
This bot requires [**pysilc 0.5**](http://developer.berlios.de/projects/python-silc/)
and the [**SILC Toolkit**](http://silcnet.org/software/download/toolkit/) (pysilc
dependancy) to work correctly.  
  
Join the channel 'qllbotsupport' with password 'helpme' for any support concerning qllbot.

## Installation ##

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

Currently qllbot does not support this function. Anyways, it is possible to run
it as a background process besides it does not support it right now. Take a look
at [**GNU Screen**](http://www.gnu.org/software/screen/).

## Writing modules ##

As written in the description of this project qllbot wants to provide an easy
way of writing modules. Nobody knows what functionality you might expect from a
bot, but with a little knowledge of Python you can write powerful modules yourself.  
  
First, let me give you a small overview: Modules are files in the ./modules/ directory
and they contain one or more commands. If
you take a look into the basic.py module, you can see three commands which are
represented by functions (get_time, calculate, say). Commands react to a certain
syntax in the chat room, like hashtag (#) + command keyword (e.g. '#key param').
If you need deeper access to chat functions an eventlistener might be the way to
go. You can find eventlistener functions in the module youtube.py. The function
'display_youtube_video_title()' reacts to the event 'channel_message' and does
not have to be called with a hashtag (#). If you are curios: youtube.py searches
for youtube links and prints out title and uploader.  

## Write a command ##

Start a new module named helloworld.py and add 'helloworld' to the MODULES list
in settings.py. First read the code:  
	#!/usr/bin/env python
	# -*- coding: utf-8 -*-
	from qllbot.Registry import *
	
	
	def print_helloworld(param):  
		''' Just for testing purposes. '''
		return u'hello world'
	
	
	add_command('hello', print_helloworld)
Okay let's analyse the code: The first two lines are just standard python stuff
(there is a shebang line, because it makes debugging easier). qllbot.Registry is
very important, because it adds functions like add_command() or subscribe() to the
module. In line 6 a python function named print_helloworld starts and it recieves
one parameter. This parameter is everything that is followed by your command as a string.  
  
Example: #hello world -> param = 'world', #hello -> param = ''.  
  
The following comment will be used as a docstring for the command. Every command
has to have a docstring! (e.g. #help hello -> Just for testing purposes.)  
  
The next line returns an unicode string. Remember: Every string you return will
be sent to the channel. If you don't return a string or you return an empty string,
nothing will be sent.  
  
The last line sets a command key for your function. Here the function print_helloworld
is mapped to the command key 'hello'. Here is the command in action:  
	(02:38:22) qll_ext: #hello  
	(02:38:22) testbot#2: hello world  
It is allowed to map multiple command keys to the same function (see #google or #g).  

## Troubleshooting ##

1. Do you get an ascii error when returning a string in a command? Try unicode
strings or use string.encode('utf-8') before returning it.



