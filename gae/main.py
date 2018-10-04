#!/usr/bin/env python

import webapp2
from webapp2_extras import mako
from google.appengine.api import mail, users
from google.appengine.ext import db

class BaseHandler(webapp2.RequestHandler):
	@webapp2.cached_property
	def mako(self):
		return mako.get_mako(app=self.app)

	def render_response(self, _template, **context):
		rv = self.mako.render_template(_template, users=users, user=users.get_current_user(), **context)
		self.response.write(rv)

class MainHandler(BaseHandler):
	def get(self):
		self.render_response('home.html')

app = webapp2.WSGIApplication([
	('/', MainHandler)
], debug=True)
