import MySQLdb
import auth

class Database:
	conn = None
	cur = None

	def __init__(self):
		self.conn = MySQLdb.connect(host=auth.DB_HOST, user=auth.DB_USER, passwd=auth.DB_PASS, db=auth.DB_NAME)
		self.cur = self.conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)

	def query(self, query):
		self.cur.execute(query)
		self.conn.commit()

	def fetch(self):
		return self.cur.fetchall()

	def close(self):
		self.cur.close()
