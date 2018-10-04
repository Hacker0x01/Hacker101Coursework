#!/usr/bin/env python

import datetime, hashlib, random, re, webapp2
from webapp2_extras import mako, sessions
from google.appengine.api import mail, users
from google.appengine.ext import db

class Profile(db.Model):
	user = db.UserProperty()
	nickname = db.TextProperty()
	desc = db.TextProperty()
	pic = db.TextProperty()

	def html_desc(self):
		def rep(match):
			sub = match.group(1)
			if '|' not in sub:
				return '[' + sub + ']'
			else:
				color, text = sub.split('|', 1)
				color = color.replace('<', '\0')
				color = color.replace('>', '\x02')
				color = color.replace('"', '\x01')
				return '\0span style=\x01color: %s\x01\x02%s\x00/span\x02' % (color.strip(), text.strip())
		desc = re.sub(r'\[(.*?)\]', rep, self.desc)
		desc = desc.replace('<', '&lt;')
		desc = desc.replace('>', '&gt;')
		desc = desc.replace('"', '&quot;')
		desc = desc.replace('\0', '<')
		desc = desc.replace('\x02', '>')
		desc = desc.replace('\x01', '"')
		desc = desc.replace('\n', '<br>')
		return desc

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
		id = self.request.get('id')
		if id:
			try:
				profile = Profile.get_by_id(int(id))
			except:
				profile = None
			if profile == None:
				self.response.write('Unknown ID ' + id)
				return
		else:
			profiles = list(Profile.all().filter('user =', users.get_current_user()).run())
			if len(profiles) == 0:
				profile = Profile(
					user=users.get_current_user(),
					nickname=users.get_current_user().nickname(),
					desc='[ red | All ] [ orange | the ] [ yellow | colors ]\n[ green | of ] [ blue | the ] [ purple | rainbow! ]',
					pic='http://breaker-studentcenter.appspot.com/favicon.png'
				)
				profile.put()
			else:
				profile = profiles[0]

		self.render_response('level2/home.html', profile=profile, editable=profile.user == users.get_current_user())

class EditHandler(BaseHandler):
	def get(self):
		profile = list(Profile.all().filter('user =', users.get_current_user()).run())[0]

		self.render_response('level2/edit.html', profile=profile, id=self.request.get('id'))

	def post(self):
		if self.request.get('csrf') != self.csrf:
			self.response.write('Bad CSRF token')
			return

		pic = self.request.get('pic')
		if not '.' in pic or pic.rsplit('.', 1)[1].lower() not in ('png', 'jpg', 'jpeg', 'ico'):
			self.response.write('Profile picture must be PNG, JPG, or ICO!')
			return

		profile = list(Profile.all().filter('user =', users.get_current_user()).run())[0]
		profile.nickname = self.request.get('nickname')
		profile.pic = pic
		profile.desc = self.request.get('desc')
		profile.put()

		self.redirect('/levels/2/')

config = {}
config['webapp2_extras.sessions'] = {
	'secret_key' : 'firstclass'
}

app = webapp2.WSGIApplication([
	('/levels/2/', MainHandler), 
	('/levels/2/edit', EditHandler), 
], debug=True, config=config)
