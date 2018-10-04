#!/usr/bin/env python

import datetime, hashlib, random, re, webapp2
from webapp2_extras import mako, sessions
from google.appengine.api import mail, users
from google.appengine.ext import db

class Story(db.Model):
	user = db.UserProperty()
	title = db.TextProperty()
	link = db.TextProperty()
	votes = db.IntegerProperty()

	@property
	def domain(self):
		return '.'.join(self.link.split('://', 1)[1].split('/', 1)[0].rsplit('.', 2)[-2:])

	@property
	def comments(self):
		return list(Comment.all().filter('story =', self).order('-votes').run())

class User(db.Model):
	user = db.UserProperty()
	karma = db.IntegerProperty()
	votes = db.ListProperty(long)

	def voted_on(self, id):
		return id in self.votes

class Comment(db.Model):
	user = db.UserProperty()
	votes = db.IntegerProperty()
	content = db.TextProperty()
	story = db.ReferenceProperty(Story)

class BaseHandler(webapp2.RequestHandler):
	@webapp2.cached_property
	def mako(self):
		return mako.get_mako(app=self.app)

	def dispatch(self):
		dusers = list(User.all().filter('user =', users.get_current_user()).run())
		if len(dusers):
			self.dbuser = dusers[0]
		else:
			self.dbuser = User(user=users.get_current_user(), karma=0)
			self.dbuser.put()

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
		rv = self.mako.render_template(_template, page_url=self.request.url, users=users, user=users.get_current_user(), dbuser=self.dbuser, csrf=self.csrf, **context)
		self.response.write(rv)

class MainHandler(BaseHandler):
	def get(self):
		stories = list(Story.all().run())
		self.render_response('level4/home.html', stories=stories, curuser=self.dbuser)

class SubmitHandler(BaseHandler):
	def get(self):
		self.render_response('level4/submit.html', curuser=self.dbuser)

	def post(self):
		if self.request.get('csrf') != self.csrf:
			self.response.write('Invalid CSRF token!')
			return

		link = self.request.get('link')
		if not link.lower().startswith('http://') and not link.lower().startswith('https://'):
			self.response.write('Link must be http or https.')
			return

		story = Story(
				user=users.get_current_user(), 
				title=self.request.get('title')[:80], 
				link=link, 
				votes=1
			)
		story.put()

		self.redirect('/levels/4/')

class VoteHandler(BaseHandler):
	def get(self):
		id = int(self.request.get('id'))
		type = globals()[self.request.get('type')]
		obj = type.get_by_id(id)

		if self.dbuser.voted_on(id):
			self.redirect(str(self.request.get('from')))
			return

		self.dbuser.votes.append(id)
		self.dbuser.put()

		if type == Story:
			change = 1
		else:
			change = int(self.request.get('change'))
			if change < 0:
				change = -1
			else:
				change = 1

		obj.votes += change
		obj.put()
		user = list(User.all().filter('user =', obj.user).run())[0]
		user.karma += change
		user.put()

		self.redirect(str(self.request.get('from')))

class DeleteHandler(BaseHandler):
	def get(self):
		self.render_response('level4/delete.html', curuser=self.dbuser, id=self.request.get('id'), type=self.request.get('type'), _from=self.request.get('from'))

	def post(self):
		id = int(self.request.get('id'))
		type = globals()[self.request.get('type')]
		obj = type.get_by_id(id)

		if obj.user != users.get_current_user():
			self.response.write("Cannot delete other users' posts")
			return

		obj.delete()

		if type == Story and '/comments?' in self.request.get('from'):
			self.redirect('/levels/4/')
		else:
			self.redirect(str(self.request.get('from')))

class CommentHandler(BaseHandler):
	def get(self):
		story = Story.get_by_id(int(self.request.get('id')))
		self.render_response('level4/comments.html', curuser=self.dbuser, story=story)

	def post(self):
		if self.request.get('csrf') != self.csrf:
			self.response.write('Mismatched CSRF token')
			return

		id = self.request.get('id')
		comment = Comment(
				user=users.get_current_user(), 
				story=Story.get_by_id(int(id)),
				votes=1, 
				content=self.request.get('comment')
			)
		comment.put()
		self.redirect('/levels/4/comments?id=' + id)

config = {}
config['webapp2_extras.sessions'] = {
	'secret_key' : 'paodsjfpsdojfasdpofjsdpfosdjafpwme;lcme;aclm;jp;avra'
}

app = webapp2.WSGIApplication([
	('/levels/4/', MainHandler), 
	('/levels/4/submit', SubmitHandler), 
	('/levels/4/vote', VoteHandler), 
	('/levels/4/comments', CommentHandler), 
	('/levels/4/delete', DeleteHandler), 
], debug=True, config=config)
