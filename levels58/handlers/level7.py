from handler import *

@handler('level7/index')
def get_index(error=None, username='admin', password=''):
	return dict(error=error, username=username, password=password)

@handler
def post_index(username, password):
	try:
		user = db.query("SELECT password FROM users WHERE username='%s'" % username)
	except Exception, e:
		import traceback
		return Response(traceback.format_exc() + '\n' + e[1], mimetype='text/plain')

	if len(user) == 0:
		redirect(get_index.url(error='User does not exist', username=username, password=password))
	elif user[0][0] == password:
		redirect(get_success.url(username=username))
	else:
		redirect(get_index.url(error='Invalid password', username=username, password=password))

@handler('level7/success')
def get_success(username):
	return dict(username=username)

if not db.hastable('users'):
	db.maketable('users', 
		username='VARCHAR(1024)', 
		password='VARCHAR(1024)'
	)
