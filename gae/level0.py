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
		to, amount = self.request.get('to') or '', self.request.get('amount') or ''

		acct = sum(map(ord, users.get_current_user().nickname()))

		self.render_response('level0/home.html', acct_num=acct, to=to, amount=amount)

	def post(self):
		acct = sum(map(ord, users.get_current_user().nickname()))

		to, _from, amount = self.request.get('to'), self.request.get('from') or acct, self.request.get('amount')

		error = message = None
		if to == '' or amount == '':
			error = 'Missing to or amount fields.'
		else:
			try:
				amount, to, _from = int(amount), int(to), int(_from)
			except:
				error = 'Amount and account numbers must be integers'
			else:
				if amount > 0:
					message = 'Transferred $%i from %i%s to %i%s.' % (amount, _from, ' (you)' if _from == acct else '', to, ' (you)' if to == acct else '')
				else:
					error = 'Amounts must be greater than zero'

		self.render_response('level0/home.html', acct_num=str(acct), to='' if not error else str(to), amount='' if not error else str(amount), message=message, error=error)

app = webapp2.WSGIApplication([
	('/levels/0/', MainHandler)
], debug=True)
