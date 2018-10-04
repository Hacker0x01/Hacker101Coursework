import os
from json import dumps
from flask import abort, make_response, render_template, request, session, Response
from flask import redirect as _redirect
from werkzeug.exceptions import HTTPException
from urllib import quote, urlencode
from db import db
from datetime import datetime

class DictObject(dict):
	pass

class StrObject(str):
	pass

all = {}

def handler(_tpl=None, _json=False, CSRFable=False):
	def sub(func):
		ofunc = func
		while hasattr(func, '__delegated__'):
			func = func.__delegated__
		sofunc = func

		name = func.func_name
		rpc = False
		tpl = _tpl
		json = _json
		if name.startswith('get_'):
			name = name[4:]
			method = 'GET'
		elif name.startswith('post_'):
			method = 'POST'
		elif name.startswith('rpc_'):
			method = 'POST'
			rpc = json = True
			tpl = None
		else:
			raise Exception('All handlers must be marked get_, post_, or rpc_.')

		module = func.__module__.split('.')[-1]
		if not module in all:
			all[module] = DictObject()
			setattr(handler, module, all[module])
		args = func.__code__.co_varnames[:func.__code__.co_argcount]
		hasId = len(args) > 0 and args[0] == 'id' and not rpc

		def func(id=None):
			if 'csrf' not in session:
				token = os.urandom(16)
				session['csrf'] = ''.join('%02x' % ord(c) for c in token)
			if not CSRFable and method == 'POST' and \
				('csrf' not in request.form or request.form['csrf'] != session['csrf']):
				abort(403)
			params = request.form if method == 'POST' else request.args
			kwargs = {}
			for i, arg in enumerate(args):
				if i == 0 and arg == 'id' and not rpc:
					continue
				if arg in params:
					kwargs[arg] = params[arg]
				elif arg in request.files:
					kwargs[arg] = request.files[arg]
				else:
					assert not rpc # RPC requires all arguments.

			try:
				if hasId and id != None:
					ret = ofunc(int(id), **kwargs)
				else:
					ret = ofunc(**kwargs)
			except RedirectException, r:
				return _redirect(r.url)
			if json:
				ret = dumps(ret)
			elif tpl != None:
				if isinstance(ret, str) or isinstance(ret, unicode):
					return ret
				if ret == None:
					ret = {}
				sret = ret
				ret = kwargs
				ret['handler'] = handler
				ret['request'] = request
				ret['session'] = session
				ret['len'] = len
				ret.update(sret)
				ret = render_template(tpl + '.html', **ret)
				csrf = '<input type="hidden" name="csrf" value="%s">' % session['csrf']
				ret = ret.replace('$CSRF$', csrf)

			if hasattr(request, '_headers'):
				ret = make_response(ret, 200)
				for k, v in request._headers.items():
					ret.headers[k] = v

			return ret

		func.func_name = '__%s__%s__' % (module, name)

		def url(_id=None, **kwargs):
			if module == 'index':
				url = '/'
				trailing = True
			else:
				url = '/%s' % module
				trailing = False
			if name != 'index':
				if not trailing:
					url += '/'
				url += '%s' % name
				trailing = False
			if _id != None:
				if not trailing:
					url += '/'
				url += quote(str(_id))
			if len(kwargs):
				url += '?'
				url += urlencode(dict((k, str(v)) for k, v in kwargs.items()))
			return url

		ustr = StrObject(url())
		ustr.__call__ = ofunc
		ustr.url = url
		func.url = url
		if not name in all[module]:
			all[module][name] = method, args, rpc, [None, None]
		if hasId and not rpc:
			all[module][name][3][1] = func
		else:
			all[module][name][3][0] = func
		setattr(all[module], sofunc.func_name, ustr)
		return ustr

	if _tpl != None and hasattr(_tpl, '__call__'):
		func = _tpl
		_tpl = None
		return sub(func)
	return sub

def sessid():
	if 'sessid' not in session:
		token = os.urandom(8)
		session['sessid'] = ''.join('%02x' % ord(c) for c in token)
	return session['sessid']
handler.sessid = sessid

def header(key, value):
	if not hasattr(request, '_headers'):
		request._headers = {}

	request._headers[key] = value
handler.header = header

class RedirectException(Exception):
	def __init__(self, url):
		self.url = url

def redirect(url, _id=None, **kwargs):
	if hasattr(url, '__call__') and hasattr(url, 'url'):
		url = url.url(_id, **kwargs)
	print 'Redirecting to', url
	raise RedirectException(url)

def exam1_auth(level, check=False):
	if check:
		if 'userid' not in session:
			return False

		iso, dlevel = db.query('SELECT creation, level FROM exam1_users WHERE id=%s', session['userid'])[0]
		try:
			date = datetime.strptime(iso, '%Y-%m-%dT%H:%M:%S')
		except:
			date = datetime.strptime(iso, '%Y-%m-%dT%H:%M:%S.%f')

		if dlevel < level:
			return False

		if (datetime.now() - date).total_seconds() > 14400:
			return False

		return True

	def xsub(func):
		def sub(*args, **kwargs):
			if 'userid' not in session:
				redirect(handler.exam1.get_index.url(error='Session expired'))

			iso, dlevel = db.query('SELECT creation, level FROM exam1_users WHERE id=%s', session['userid'])[0]
			try:
				date = datetime.strptime(iso, '%Y-%m-%dT%H:%M:%S')
			except:
				date = datetime.strptime(iso, '%Y-%m-%dT%H:%M:%S.%f')

			if dlevel < level:
				redirect(handler.exam1.get_index.url(error='You have not yet achieved this level'))

			if (datetime.now() - date).total_seconds() > 14400:
				redirect(handler.exam1.get_index.url(error='Time has expired!'))

			return func(*args, **kwargs)

		sub.__delegated__ = func
		return sub
	return xsub

int_ = int
def int(v):
	try:
		return int_(v)
	except:
		return 0
