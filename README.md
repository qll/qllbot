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
<code>
$ ./configure --without-iconv  
$ make  
\# make install
</code>  
This should install everything needed. Now you have to compile pysilc without
iconv. Just change the line <code>libraries = ['iconv', 'silc', 'silcclient'],</code>
into <code>libraries = ['silc', 'silcclient']</code> in setup.py. This caused
no problems with my installation, yet. Now build and install:  
<code>
$ python setup.py build  
\# python setup.py install  
</code>  
  
qllbot should work out of the box now. Just edit your settings.py and run it in
a terminal. Everything should work fine now.  
<code>$ python qllbot.py</code>

## Run as background process ##

Currently qllbot does not support this function. Anyways, it is possible to run
it as a background process besides it does not support it right now. Take a look
at [**GNU Screen**](http://www.gnu.org/software/screen/).

