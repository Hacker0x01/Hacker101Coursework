import commands, os
from handler import *
from glob import glob
from os.path import isfile, isdir

@handler('level5/index')
def get_index(path='/'):
	if not isdir('level5_docs/' + path):
		return 'No such directory: ' + path

	if not path.endswith('/'):
		path += '/'
	dirs = []
	files = []
	for fn in glob('level5_docs/' + path + '*'):
		if isdir(fn):
			dirs.append(fn.rsplit('/', 1)[1])
		else:
			files.append(fn.rsplit('/', 1)[1])

	return dict(path=path, dirs=dirs, files=files)

@handler
def get_read(path):
	path = path.replace('../', '')
	try:
		return Response(file('level5_docs/' + path).read(), mimetype='text/plain')
	except:
		return 'No such file: ' + path

@handler
def post_search(path, text):
	old = os.getcwd()
	try:
		os.chdir('level5_docs/' + path)
		out = commands.getoutput('grep -r "%s" .' % text)
	finally:
		os.chdir(old)
	return out.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
