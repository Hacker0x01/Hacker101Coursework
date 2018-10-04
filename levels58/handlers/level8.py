from handler import *

@handler('level8/index')
def get_index():
	return dict(docs=db.query('SELECT id, name, mimetype FROM documents WHERE sessid=%s', handler.sessid()))

@handler
def post_index(name, doc):
	fn, mime = doc.filename, doc.mimetype

	doc.save('level8_sandbox/' + fn)

	db.query("INSERT INTO documents (name, filename, mimetype, sessid) VALUES ('%s', '%s', '%s', '%s')" % (name, fn, mime, handler.sessid()))

	redirect(get_index)

inlinable = 'image/jpeg image/png text/plain'.split(' ')

@handler
def get_view(id, download='None'):
	download = eval(download)
	
	(filename, mimetype), = db.query('SELECT filename, mimetype FROM documents WHERE sessid=%s AND id=%s', handler.sessid(), id)

	if download == None and mimetype not in inlinable:
		download = True

	if download:
		handler.header('Content-Disposition', 'attachment; filename=' + filename)

	handler.header('Content-Type', mimetype)

	return file('level8_sandbox/' + filename, 'rb').read()

if not db.hastable('documents'):
	db.maketable('documents', 
		name='VARCHAR(1024)', 
		filename='VARCHAR(1024)', 
		mimetype='VARCHAR(1024)', 
		sessid='CHAR(16)'
	)
