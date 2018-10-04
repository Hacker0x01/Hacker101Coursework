from handler import *
from handler import exam1_auth as auth

@handler('exam1/el10/index')
@auth(0)
def get_index(message=None):
	return dict(message=message, posts=db.query('SELECT id, name, email, body, date FROM el10_post WHERE owner=%s ORDER BY id DESC', session['userid']))

@handler(CSRFable=True)
@auth(0)
def post_index(name, email, body):
	db.query('INSERT INTO el10_post (name, email, body, date, owner) VALUES (%s, %s, %s, %s, %s)', name, email, body, str(datetime.now()), session['userid'])

	redirect(get_index)

@handler('exam1/el10/admin_login')
@auth(0)
def get_admin_login():
	pass

@handler
@auth(0)
def post_admin_login(username, password):
	if len(db.query("SELECT id FROM el10_admins WHERE username='%s' AND password='%s'" % (username, password))):
		session['el10_admin'] = True
		if db.query('SELECT level FROM exam1_users WHERE id=%s', session['userid'])[0][0] == 0:
			db.query('UPDATE exam1_users SET level=1 WHERE id=%s', session['userid'])
			redirect(get_index.url(message='Exam 1 level 1 unlocked!'))
		else:
			redirect(get_index)
	else:
		redirect(get_admin_login)

@handler
def get_admin_logout():
	session['el10_admin'] = False
	redirect(get_index)

@handler
@auth(0)
def get_delete(id):
	if len(db.query('SELECT id FROM el10_post WHERE id=%s AND owner=%s', id, session['userid'])) == 0:
		return 'Post does not exist.'

	db.query('DELETE FROM el10_post WHERE id=%s', id)

	redirect(get_index)

if not db.hastable('el10_post'):
	db.maketable('el10_post',
		name='VARCHAR(1024)', 
		email='VARCHAR(1024)', 
		body='VARCHAR(1024)', 
		date='VARCHAR(1024)', 
		owner='INT'
	)
if not db.hastable('el10_admins'):
	db.maketable('el10_admins',
		username='VARCHAR(1024)', 
		password='VARCHAR(1024)'
	)
