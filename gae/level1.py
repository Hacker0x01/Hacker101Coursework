#!/usr/bin/env python

import datetime, hashlib, re, webapp2
from webapp2_extras import mako
from google.appengine.api import mail, users
from google.appengine.ext import db

class Post(db.Model):
	by = db.UserProperty()
	contents = db.TextProperty()
	date = db.DateTimeProperty()

class BaseHandler(webapp2.RequestHandler):
	@webapp2.cached_property
	def mako(self):
		return mako.get_mako(app=self.app)

	def render_response(self, _template, **context):
		rv = self.mako.render_template(_template, users=users, user=users.get_current_user(), **context)
		self.response.write(rv)

class MainHandler(BaseHandler):
	def get(self):
		csrf = hashlib.md5(users.get_current_user().nickname()).hexdigest()
		allposts = Post.all().order('date')
		posts = []
		for i, post in enumerate(allposts):
			if post.by == users.get_current_user():
				posts.append((i, post))
		posts.reverse()
		self.render_response('level1/home.html', csrf=csrf, posts=posts)

class PostHandler(BaseHandler):
	def get(self):
		id = self.request.get('id')

		self.render_response('level1/post.html', post=Post.all().order('date')[int(id)])

	def post(self):
		if len(self.request.get('csrf')) != 32:
			self.response.write('Bad CSRF token')
			return

		status = ostatus = self.request.get('status')
		status = status.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
		message = [None]

		def rep(match):
			if '&gt;' in match.group(0):
				message[0] = "So, you can't break out of the <a> tag.  But what can you do inside the tag?"
			return '<a href="%s">%s</a>' % (match.group(0), match.group(0))
		status = re.sub(r'http://\S+', rep, status)

		Post(by=users.get_current_user(), contents=status, date=datetime.datetime.now()).put()
		
		self.render_response('level1/posted.html', message=message[0])

app = webapp2.WSGIApplication([
	('/levels/1/', MainHandler), 
	('/levels/1/post', PostHandler), 
], debug=True)
