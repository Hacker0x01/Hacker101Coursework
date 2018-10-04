#!/usr/bin/env python

import datetime, hashlib, random, re, webapp2
from webapp2_extras import mako, sessions
from google.appengine.api import mail, users
from google.appengine.ext import db

def filter_tags(text):
	def rep(match):
		text = match.group(1)
		if text[0] == '/':
			return match.group(0)
		else:
			if text.startswith('script'):
				return 'JS Detected!'
			elif text.startswith('a '):
				if len(re.findall(r'\Won\w+=', text)):
					return 'JS Detected!'
				else:
					return match.group(0)
			else:
				return match.group(0)
	return re.sub(r'<(.*?)>', rep, text)

class Page(db.Model):
	user = db.UserProperty()
	title = db.TextProperty()
	body = db.TextProperty()

	@property
	def html_body(self):
		return filter_tags(self.body).replace('\n', '<br>')

class BaseHandler(webapp2.RequestHandler):
	@webapp2.cached_property
	def mako(self):
		return mako.get_mako(app=self.app)

	def dispatch(self):
		self.session_store = sessions.get_store(request=self.request)

		try:
			webapp2.RequestHandler.dispatch(self)
		finally:
			self.session_store.save_sessions(self.response)

	@webapp2.cached_property
	def session(self):
		return self.session_store.get_session()

	@property
	def csrf(self):
		csrf = self.session.get('csrf', None)
		if csrf == None:
			csrf = ''.join('%02x' % ord(c) for c in '...Not this time!' + ''.join(chr(random.randrange(256)) for i in xrange(16)))
			self.session['csrf'] = csrf
		return csrf

	def render_response(self, _template, **context):
		rv = self.mako.render_template(_template, users=users, user=users.get_current_user(), csrf=self.csrf, **context)
		self.response.write(rv)

class MainHandler(BaseHandler):
	def get(self):
		pages = list(Page.all().filter('user =', users.get_current_user()).run())
		if len(pages) == 0:
			page = Page(
				user=users.get_current_user(),
				title='Welcome to Breaker CMS!',
				body='No content yet.  Log in as an admin to change it!'
			)
			page.put()
		else:
			page = pages[0]
		if self.request.cookies.get('admin', None) == None:
			self.response.set_cookie('admin', '0')
		self.render_response('level3/home.html', page=page)

class AdminHandler(BaseHandler):
	def get(self):
		if self.request.cookies.get('admin') != '1':
			self.response.write('Not an admin!')
			return
		page = list(Page.all().filter('user =', users.get_current_user()).run())[0]
		self.render_response('level3/admin.html', page=page)

	def post(self):
		page = list(Page.all().filter('user =', users.get_current_user()).run())[0]
		page.title = self.request.get('title')
		page.body = self.request.get('body')
		page.put()
		self.redirect('/levels/3/')

config = {}
config['webapp2_extras.sessions'] = {
	'secret_key' : 'posjdapfosdjfpdsoafjsdpofjdspvompmepofmpofj4pfowjfpojcpo4pomapojm'
}

app = webapp2.WSGIApplication([
	('/levels/3/', MainHandler), 
	('/levels/3/admin', AdminHandler), 
], debug=True, config=config)
