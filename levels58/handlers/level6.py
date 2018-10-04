from handler import *

@handler('level6/index')
def get_index(filter=''):
	if db.query('SELECT COUNT(id) FROM students WHERE sessid=%s;', handler.sessid())[0][0] == 0:
		def add(firstname, lastname):
			db.query('INSERT INTO `students` (firstname, lastname, sessid) VALUES (%s, %s, %s);', firstname, lastname, handler.sessid())

		add('John', 'Doe')
		add('Cody', 'Brocious')
		add('Testy', 'McTesterson')

	print filter
	return dict(filter=filter, students=db.query("SELECT id, lastname, firstname FROM students WHERE sessid='%s' AND (firstname LIKE '%%%%%s%%%%' OR lastname LIKE '%%%%%s%%%%');" % (handler.sessid(), filter, filter)))

@handler('level6/edit')
def get_edit(id):
	return dict(student=db.query("SELECT id, lastname, firstname FROM students WHERE id='%s';" % id)[0])

@handler
def post_edit(id, firstname, lastname):
	student = db.query('SELECT sessid FROM students where id=%s', id)
	if student[0][0] != handler.sessid():
		return 'Student does not belong to your account.'

	db.query('UPDATE students SET lastname=%s, firstname=%s WHERE id=%s', lastname, firstname, id)

	redirect(get_index)

@handler('level6/add')
def get_add():
	pass

@handler(CSRFable=True)
def post_add(firstname, lastname):
	db.query("INSERT INTO `students` (firstname, lastname, sessid) VALUES ('%s', '%s', '%s');" % (firstname, lastname, handler.sessid()))

	redirect(get_index)

if not db.hastable('students'):
	db.maketable('students', 
		lastname='VARCHAR(1024)', 
		firstname='VARCHAR(1024)', 
		sessid='CHAR(16)'
	)
