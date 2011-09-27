from qllbot.Registry import *


registry = Registry()
db = registry.db


def create_whatsup_tables():
	''' There will be a history of events stored in this table '''
	db.execute('CREATE TABLE whatsup (id INTEGER PRIMARY KEY, channel TEXT, action TEXT, active INTEGER)')

def set_whatsup(param):
	''' Tell the bot whats going on. '''
	if param == '':
		c = db.cursor()
		c.execute('SELECT id, active FROM whatsup WHERE channel = ? ORDER BY id DESC LIMIT 0,1', (registry.cmdinterpreter.current_channel,))
		result = c.fetchone()
		if result != None and result[1] != 0:
			db.execute('UPDATE whatsup SET active = 0 WHERE id = ?', (result[0],))
		return u'Nothing going on...'
	else:
		db.execute('INSERT INTO whatsup(channel, action, active) VALUES (?, ?, ?)', (registry.cmdinterpreter.current_channel, param, 1))
		return u'Saved it, dude! Ask with #whatsup or #wassup.'
		

def get_whatsup(param):
	''' If you ask this bot whats up it will response with what you have set. '''
	c = db.cursor()
	c.execute('SELECT action, active FROM whatsup WHERE channel = ? ORDER BY id DESC LIMIT 0,1', (registry.cmdinterpreter.current_channel,))
	result = c.fetchone()
	if result == None:
		return u'There really never was anything going on.'
	elif result[1] == 0: # action not active
		return u'Absolutely nothing.'
	else:
		return result[0]


subscribe('create_tables', create_whatsup_tables)

add_command('thatsup', set_whatsup)
add_command('whatsup', get_whatsup)
add_command('wassup', get_whatsup)
