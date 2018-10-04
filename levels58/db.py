import MySQLdb as mdb

sql = dict(
	host='...', 
	username='...', 
	password='...', 
	db='...'
)

class DB(object):
	def __init__(self):
		self.conn = mdb.connect(sql['host'], sql['username'], sql['password'], sql['db'])

	def query(self, query, *args):
		cursor = None
		try:
			with self.conn:
				cursor = self.conn.cursor()
				print '[DEBUG] %s <= %r' % (query, args)
				cursor.execute(query, args)

				return cursor.fetchall()
		except mdb.OperationalError, e:
			try:
				if cursor is not None:
					cursor.close()
			except:
				pass
			if 'server has gone away' in str(e):
				self.conn = mdb.connect(sql['host'], sql['username'], sql['password'], sql['db'])
				return self.query(query, *args)
			else:
				raise

	def hastable(self, table):
		try:
			print 'Checking to see if table %s exists' % table
			self.query('SELECT id FROM `%s` LIMIT 1;' % table)
			print 'Successful query ... ?'
			return True
		except:
			import traceback
			traceback.print_exc()
			return False

	def maketable(self, table, **kwargs):
		if len(kwargs):
			elems = ', ' + ', '.join('%s %s' % (k, v) for k, v in kwargs.items())
		else:
			elems = ''
		self.query('CREATE TABLE `%s`(id int not null auto_increment, primary key(id)%s);' % (table, elems))

db = DB()
