from qllbot.Registry import *
from qllbot.basic_functions import get_username


registry = Registry()
db = registry.db


def create_whatsup_tables():
	''' There will be a history of events stored in this table '''
	db.execute('CREATE TABLE whatsup (id INTEGER PRIMARY KEY, channel TEXT, action TEXT, active INTEGER)')
	db.execute('CREATE TABLE whatsup_users (whatsup_id INTEGER, username TEXT)')

def set_whatsup(param):
	''' Tell the bot whats going on. '''
	if param == '':
		c = db.cursor()
		c.execute('SELECT id, active FROM whatsup WHERE channel = ? ORDER BY id DESC LIMIT 0,1', (registry.cmdinterpreter.current_channel,))
		result = c.fetchone()
		if result != None and result[1] != 0:
			db.execute('UPDATE whatsup SET active = 0 WHERE id = ?', (result[0],))
			registry.client.set_topic(registry.cmdinterpreter.current_channel, '')
		return u'Nothing going on...'
	else:
		db.execute('INSERT INTO whatsup(channel, action, active) VALUES (?, ?, ?)', (registry.cmdinterpreter.current_channel, param, 1))
		registry.client.set_topic(registry.cmdinterpreter.current_channel, param)
		return u'Saved it, dude! Ask #whatsup or #wassup.'
		
def get_whatsup(param):
	''' If you ask this bot whats up it will response with what you have set. '''
	c = db.cursor()
	c.execute('SELECT id, action, active FROM whatsup WHERE channel = ? ORDER BY id DESC LIMIT 0,1', (registry.cmdinterpreter.current_channel,))
	result = c.fetchone()
	if result == None:
		return u'There really never was anything going on.'
	elif result[2] == 0: # action not active
		return u'Absolutely nothing.'
	else:
		c.execute('SELECT username FROM whatsup_users WHERE whatsup_id = ?', (result[0],))
		all_results = c.fetchall()
		if len(all_results) > 0:
			users = [user[0] for user in all_results]
			return u'%s\nwith %s' % (result[1], ", ".join(users))
		else:
			return result[1]

def join_action(param):
	''' Adds you or the person in the parameter to the current activity that is going on (see #whatsup). '''
	c = db.cursor()
	c.execute('SELECT id, active FROM whatsup WHERE channel = ? ORDER BY id DESC LIMIT 0,1', (registry.cmdinterpreter.current_channel,))
	result = c.fetchone()
	if result != None and result[1] != 0:
		if param == '':
			param = get_username(registry.cmdinterpreter.current_sender)
		c.execute('SELECT whatsup_id FROM whatsup_users WHERE whatsup_id = ? AND username = ?', (result[0], param))
		if c.fetchone() == None:
			db.execute('INSERT INTO whatsup_users VALUES (?, ?)', (result[0], param))
			return get_whatsup('')
		else:
			return u'%s is already in the list!' % param

def leave_action(param):
	''' Removes you or the person in the parameter  from the list of users who participate in an action set by #thatsup. '''
	c = db.cursor()
	c.execute('SELECT id, active FROM whatsup WHERE channel = ? ORDER BY id DESC LIMIT 0,1', (registry.cmdinterpreter.current_channel,))
	result = c.fetchone()
	if result != None and result[1] != 0:
		if param == '':
			param = get_username(registry.cmdinterpreter.current_sender)
		db.execute('DELETE FROM whatsup_users WHERE whatsup_id = ? AND username = ?', (result[0], param))
	return get_whatsup('')


subscribe('create_tables', create_whatsup_tables)

add_command('thatsup', set_whatsup)
add_command('whatsup', get_whatsup)
add_command('wassup',  get_whatsup)
add_command('metoo',   join_action)
add_command('+',       join_action)
add_command('-',       leave_action)
