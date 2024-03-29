import os
import sqlite3
from common import settings, util, xdg

from datetime import datetime


# Blabla ff 

class DB():
	NOW = "strftime('%Y-%m-%d %H:%M:%S','now')";
	
	LIMIT_PER_FILE = 100
	
	def __init__(self, fileName):
		db_path = os.path.join(xdg.get_data_home(), fileName)
		if os.path.exists(db_path):
			self.conn = sqlite3.connect(db_path)
			self.conn.row_factory = sqlite3.Row
			self.c = self.conn.cursor()
			self.createTables(True)
		else:
			self.conn = sqlite3.connect(db_path)
			self.conn.row_factory = sqlite3.Row
			self.c = self.conn.cursor()
			self.createTables()
			
	def createTables(self, newOnly=False):
		if not newOnly:
			# ***** Music *****
			self.c.execute('''CREATE TABLE files_backup
			(ID INTEGER PRIMARY KEY AUTOINCREMENT, path text, content text, birth_date datetime NOT NULL, unsaved BOOLEAN DEFAULT 0, Type_ID INTEGER
			)''')
		
		
	def addBackup(self, params):
		
		now = datetime.utcnow()
 
		print("now =", now)

		# dd/mm/YY H:M:S
		
		dt_string_type3 = now.strftime("%Y/%m/%d %H")
		dt_string_type2 = now.strftime("%Y/%m/%d")
		print(dt_string_type3)
		
		path = params[0]
		unsaved = params[2]
		type = params[3]
		
		
		limit_saved = settings.get_option('autobackup/max_number_revisions_saved_per_file', 50)
		
		
		limit_unsaved = settings.get_option('autobackup/max_number_revisions_unsaved_per_file', 50)
		
		if(unsaved == 1):
			DB.LIMIT_PER_FILE = limit_unsaved
		else:
			DB.LIMIT_PER_FILE = limit_saved
			
		
		type1_delete_after = settings.get_option('autobackup/auto_delete_revisions_after_days', 90)
		
		
		query = '''INSERT INTO files_backup (path, content, birth_date, unsaved, Type_ID) VALUES (?, ?, ''' + DB.NOW + ''', ?, ?)'''
		self.c.execute(query, params)
		self.conn.commit()
		
		
		# GLOBAL CLEAN
		query = ''' DELETE FROM files_backup WHERE birth_date <  DATETIME('now', ?) AND unsaved = ? AND Type_ID = 1'''
		# self.c.execute(query, ['-' + str(type3_delete_after) + ' day', params[0], 0])
		self.c.execute(query, ['-' + str(type1_delete_after) + ' day', unsaved])
		
		query = '''SELECT ID  FROM files_backup WHERE path = ? AND unsaved = ? ORDER BY birth_date ASC'''
		self.c.execute(query, [params[0], params[2]])
		
		
		
		
		
		
		
		
		rows = self.c.fetchall()
		print("number of rows", len(rows))
		if(len(rows) > DB.LIMIT_PER_FILE):
			IDS = []
			for i in range(len(rows) - DB.LIMIT_PER_FILE):
				IDS.append(rows[i]['ID'])
			
			if(len(IDS) > 0):
				self.deleteRevisions(IDS)
				
				
		# TYPE 2 - hours
		type2_per_basis = settings.get_option('autobackup/type2_keep_one_revision_per', 1)
		type2_delete_after = settings.get_option('autobackup/type2_auto_delete_revisions_after', 365)
		
		if(unsaved == 0 and type2_per_basis > 0):
			
			# GLOBAL CLEAN
			query = ''' DELETE FROM files_backup WHERE birth_date <  DATETIME('now', ?) AND unsaved = ? AND Type_ID = 2'''
			# self.c.execute(query, ['-' + str(type3_delete_after) + ' day', params[0], 0])
			self.c.execute(query, ['-' + str(type2_delete_after) + ' day', 0])
			# self.conn.commit()
			
			
			# query = ''' SELECT ID FROM files_backup WHERE strftime('%Y/%m/%d %H', birth_date) = ? AND path = ? AND unsaved = ?'''
			query = ''' DELETE FROM files_backup WHERE strftime('%Y/%m/%d', birth_date) = ? AND path = ? AND unsaved = ? AND Type_ID = 2'''
			self.c.execute(query, [dt_string_type2, params[0], 0])
			self.conn.commit()
			
			query = '''INSERT INTO files_backup (path, content, birth_date, unsaved, Type_ID) VALUES (?, ?, ''' + DB.NOW + ''', ?, ?)'''
			self.c.execute(query, [params[0], params[1], params[2], 2])
			self.conn.commit()
				
		
		# TYPE 3 - hours
		type3_per_basis = settings.get_option('autobackup/type3_keep_one_revision_per', 0)
		type3_delete_after = settings.get_option('autobackup/type3_auto_delete_revisions_after', 100)
		
		if(unsaved == 0 and type3_per_basis > 0):
			
			# GLOBAL CLEAN
			query = ''' DELETE FROM files_backup WHERE birth_date <  DATETIME('now', ?) AND unsaved = ? AND Type_ID = 3'''
			# self.c.execute(query, ['-' + str(type3_delete_after) + ' day', params[0], 0])
			self.c.execute(query, ['-' + str(type3_delete_after) + ' hour', 0])
			# self.conn.commit()
			
			
			# query = ''' SELECT ID FROM files_backup WHERE strftime('%Y/%m/%d %H', birth_date) = ? AND path = ? AND unsaved = ?'''
			query = ''' DELETE FROM files_backup WHERE strftime('%Y/%m/%d %H', birth_date) = ? AND path = ? AND unsaved = ? AND Type_ID = 3'''
			self.c.execute(query, [dt_string_type3, params[0], 0])
			self.conn.commit()
			
			query = '''INSERT INTO files_backup (path, content, birth_date, unsaved, Type_ID) VALUES (?, ?, ''' + DB.NOW + ''', ?, ?)'''
			self.c.execute(query, [params[0], params[1], params[2], 3])
			self.conn.commit()
			
			
			# p.birth_date > DATETIME(\'now\', \'-30 day\')
			
			
			
		
		
		
		
		
		
	def deleteAllRevisions(self):
		self.c.execute('DELETE FROM files_backup')
		self.conn.commit()
		
	def deleteRevisions(self, IDS):
		
		self.c.execute('DELETE FROM files_backup WHERE ID IN (%s)' % ("?," * len(IDS))[:-1], IDS)
		self.conn.commit()
		
		
	def getLastRevision(self, path, unsaved=1):
		query = '''SELECT content FROM files_backup WHERE path = ? AND unsaved = ? ORDER BY birth_date DESC'''
		params = [path, unsaved]
		self.c.execute(query, params)
		
		row = self.c.fetchone()
		
		if row != None:
			return row['content']
			
			
	def getRevisionContent(self, ID):
		query = '''SELECT content FROM files_backup WHERE ID = ?'''
		params = [ID]
		self.c.execute(query, params)
		
		row = self.c.fetchone()
		
		if row != None:
			return row['content']
		
	def getAllRevisions(self):
		query = '''SELECT ID, path, birth_date, unsaved, Type_ID FROM files_backup ORDER BY birth_date DESC, ID DESC'''
		
		self.c.execute(query)
		
		return self.c.fetchall()
		
		
		
