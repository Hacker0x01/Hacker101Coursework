from handler import *
from handler import exam1_auth as auth

@handler('exam1/index')
def get_index(error=None):
	if auth(0, check=True):
		redirect(get_authed)
	return dict(error=error)

@handler
def post_create_user(username, password, confirm):
	if db.query('SELECT COUNT(id) FROM exam1_users WHERE username=%s', username)[0][0] == 1:
		redirect(get_index.url(error='Username is taken'))

	if password != confirm:
		redirect(get_index.url(error='Passwords do not match'))

	db.query('INSERT INTO exam1_users (username, password, creation, level) VALUES (%s, %s, %s, 0)', username, password, datetime.now().isoformat())

	session['userid'] = db.query('SELECT id FROM exam1_users WHERE username=%s', username)[0][0]

	redirect(get_authed)

@handler
def post_login(username, password):
	data = db.query('SELECT id FROM exam1_users WHERE username=%s AND password=%s', username, password)
	if len(data) == 1:
		session['userid'] = data[0][0]
		redirect(get_authed)
	else:
		redirect(get_index.url(error='Username/password incorrect'))

@handler('exam1/authed')
@auth(0)
def get_authed():
	iso, level = db.query('SELECT creation, level FROM exam1_users WHERE id=%s', session['userid'])[0]
	try:
		date = datetime.strptime(iso, '%Y-%m-%dT%H:%M:%S')
	except:
		date = datetime.strptime(iso, '%Y-%m-%dT%H:%M:%S.%f')
	delta = 14400 - (datetime.now() - date).seconds
	return dict(hours=delta // 60 // 60, minutes=(delta // 60) % 60, level=level)

if not db.hastable('exam1_users'):
	db.maketable('exam1_users', 
		username='VARCHAR(1024)', 
		password='VARCHAR(1024)', 
		creation='VARCHAR(1024)', 
		level='INT', 
	)
