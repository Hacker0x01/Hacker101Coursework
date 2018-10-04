from handler import *
from handler import exam1_auth as auth
import os, re

def format(body):
	def rep(match):
		title = match.group(1)
		return '<a href=/el12?page=%s>%s</a>' % (title, title)
	body = body.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
	body = re.sub(r'\[\[(.*?)\]\]', rep, body)
	return body.replace('\n', '<br>')

@handler('exam1/el12/index')
@auth(2)
def get_index(page='Home'):
	path = 'el12_sandbox/%i/%s' % (session['userid'], page)
	if page == 'Home' and not os.path.exists(path):
		try:
			os.mkdir('el12_sandbox/%i' % session['userid'])
		except:
			pass
		with file(path, 'w') as fp:
			fp.write('Welcome to [[BreakerWiki]]!\n\nEnjoy your time here.')
	if os.path.exists(path):
		return dict(found=True, page=page, body=format(file(path, 'r').read()))
	else:
		return dict(found=False, page=page)

@handler('exam1/el12/edit')
@auth(2)
def get_edit(page):
	path = 'el12_sandbox/%i/%s' % (session['userid'], page)
	if not os.path.exists(path):
		redirect(get_create.url(page=page))
	return dict(body=file(path).read())

@handler
@auth(2)
def post_edit(page, body):
	if '../' in page:
		if db.query('SELECT level FROM exam1_users WHERE id=%s', session['userid'])[0][0] == 2:
			db.query('UPDATE exam1_users SET level=3 WHERE id=%s', session['userid'])
		return 'Writing to files outside the sandbox is forbidden.  But level 3 is now unlocked!'

	with file('el12_sandbox/%i/%s' % (session['userid'], page), 'w') as fp:
		fp.write(body)

	redirect(get_index.url(page=page))

@handler('exam1/el12/create')
@auth(2)
def get_create(page=''):
	pass
