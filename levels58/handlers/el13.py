from handler import *
from handler import exam1_auth as auth

@handler('exam1/el13/index')
@auth(3)
def get_index(message=None):
	pass

@handler
@auth(3)
def post_message(name, message):
	db.query("INSERT INTO el13_messages (owner, name, message) VALUES (%i, '%s', '%s')" % (session['userid'], name, message))

	redirect(get_index.url(message='Message received!'))

@handler('exam1/el13/login')
@auth(3)
def get_login():
	pass

@handler
@auth(3)
def post_login(username, password):
	if len(db.query("SELECT id FROM el13_admins WHERE username=%s AND password=%s", username, password)):
		redirect(get_feedback)
	else:
		redirect(get_login)

@handler('exam1/el13/feedback')
@auth(3)
def get_feedback():
	return dict(messages=db.query('SELECT name, message FROM el13_messages ORDER BY id DESC'))

if not db.hastable('el13_messages'):
	db.maketable('el13_messages',
		owner='INT', 
		name='VARCHAR(1024)', 
		message='VARCHAR(1024)'
	)

if not db.hastable('el13_admins'):
	db.maketable('el13_admins',
		username='VARCHAR(1024)', 
		password='VARCHAR(1024)'
	)
