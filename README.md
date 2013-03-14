# qllbot - Python powered IRC bot #
  
License: [**BSD**](http://opensource.org/licenses/bsd-license.php)

This bot requires Python 3 to work properly.

Check the [**qllbot wiki**](https://github.com/qll/qllbot/wiki) if you have any
questions or want to learn how to develop modules. It is super simple!

Feel free to email me if you need support.

## Configuration & first run ##

There is not much configuration required to get the bot started, just check the
settings.py. Most of the default settings should be okay and everything is well
documented, so you will know what you change if you change something.

You can start the bot with <code>$ python3 qllbot.py</code> and it will connect
to the IRC-Server you have set up.

## Run as background process ##

Forking qllbot to a background process is as simple as adding the -d flag to its
parameters. Example: <code>$ python3 qllbot.py -d</code>. 
