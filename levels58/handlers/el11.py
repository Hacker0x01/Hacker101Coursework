from handler import *
from handler import exam1_auth as auth
import commands

@handler('exam1/el11/index')
@auth(1)
def get_index(message=None):
	if len(getsettings()) == 0:
		savesettings(dict(
			ssid='breaksys', 
			int_ip='192.168.1.100', 
			admin_username='admin', 
			admin_password='admin'
		))
	return dict(admin='el11_admin' in session and session['el11_admin'], message=message, settings=getsettings())

@handler
@auth(1)
def post_login(username, password):
	settings = getsettings()
	if username == settings['admin_username'] and password == settings['admin_password']:
		session['el11_admin'] = True
	redirect(get_index)

@handler
@auth(1)
def get_logout():
	session['el11_admin'] = False
	redirect(get_index)

@handler(CSRFable=True)
@auth(1)
def post_set(k, v):
	savesettings({k : v})

	if 'el11_admin' not in session or session['el11_admin'] == False:
		if db.query('SELECT level FROM exam1_users WHERE id=%s', session['userid'])[0][0] == 1:
			db.query('UPDATE exam1_users SET level=2 WHERE id=%s', session['userid'])
			redirect(get_index.url(message='Exam 1 level 2 unlocked!'))

	redirect(get_index)

@handler
@auth(1)
def get_diag(cmd, param0='', param1='', param2='', param3=''):
	def escape(param):
		return param.replace('"', '\\"')
	args = [cmd, param0, param1, param2, param3]
	args = ['"%s"' % escape(arg) for arg in args if arg != '']
	return commands.getoutput(' '.join(args)).replace('\n', '\n<br>')

def getsettings():
	return dict((k, v) for k, v in db.query('SELECT _key, value FROM el11_settings WHERE owner=%s', session['userid']))

def savesettings(settings):
	for k, v in settings.items():
		if len(db.query('SELECT value FROM el11_settings WHERE owner=%s AND _key=%s', session['userid'], k)):
			db.query('UPDATE el11_settings SET value=%s WHERE owner=%s AND _key=%s', v, session['userid'], k)
		else:
			db.query('INSERT INTO el11_settings (owner, _key, value) VALUES (%s, %s, %s)', session['userid'], k, v)

if not db.hastable('el11_settings'):
	db.maketable('el11_settings', 
		owner='INT', 
		_key='VARCHAR(1024)', 
		value='VARCHAR(1024)'
	)
