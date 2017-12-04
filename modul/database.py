import sqlite3, tempfile, subprocess
import os, getpass, json
import numpy as np

class database:
	def __init__(self, setting=None, label=None, data=None, selection=None):
		self.database_name = 'database.sqlite3'
		if setting == None:
			self.setting =  '''
				CREATE TABLE `settings` (
					`id`	integer NOT NULL PRIMARY KEY AUTOINCREMENT,
					`name`	varchar ( 50 ) NOT NULL,
					`note`	text,
					`value`	text NOT NULL
				);
				'''
		else:
			self.setting = setting
		if label == None:
			self.label = '''
				CREATE TABLE `label` (
					`id`		integer NOT NULL PRIMARY KEY AUTOINCREMENT,
					`name`		varchar ( 50 ) NOT NULL,
					`language`	varchar ( 5 ) NOT NULL,
					`zpl`		text NOT NULL,
					`note`		text
				);
				'''
		else:
			self.label = label
		if selection == None:
			self.selection = '''
				CREATE TABLE `selection` (
					`id`		integer NOT NULL PRIMARY KEY AUTOINCREMENT,
					`name`		varchar ( 50 ) NOT NULL,
					`type`		varchar ( 3 ) NOT NULL,
					`value`		text
				);
				'''
		else:
			self.selection = selection
		if data == None:
			self.data = '''
				CREATE TABLE `data` (
					`id`		integer NOT NULL PRIMARY KEY AUTOINCREMENT,
					`EAN`		integer NOT NULL,
					`label`		varchar ( 50 ),
					`code`		varchar ( 50 ),
					`ecode`		varchar ( 50 )
				);
				'''
		else:
			self.data = data

	def __create(self):
		conn = sqlite3.connect(self.database_name)
		c = conn.cursor()
		c.execute(self.setting)
		c.execute(self.label)
		c.execute(self.selection)
		c.execute(self.data)
		conn.commit()
		conn.close()

	def init(self):
		if os.path.exists(self.database_name):
			print('database already exists')
			return False
		else:
			self.__create()
			return True

	def __write(self, sql):
		conn = sqlite3.connect(self.database_name)
		c = conn.cursor()
		c.execute(sql)
		conn.commit()
		conn.close()

	def __read(self, sql):
		conn = sqlite3.connect(self.database_name)
		c = conn.cursor()
		c.execute(sql)
		data = c.fetchall()
		conn.commit()
		conn.close()
		return data

	def __add(self, column_name, datatype, selection):
		addC = 'ALTER TABLE data ADD {0} {1};'
		addS = 'INSERT INTO selection (name, type, value) VALUES ("{0}", "{1}", {2});'
		try:
			self.__write(addC.format(column_name, datatype))
			if datatype == 'integer':
				self.__write(addS.format(column_name, 'int', selection))
			elif datatype == 'decimal':
				self.__write(addS.format(column_name, 'dec', selection))
			else:
				self.__write(addS.format(column_name, 'str', selection))
			print(column_name+' was added successfully')
		except Exception as e:
			print(column_name+'\n\t'+str(e))

	def addColumn(self):
		add = []
		while True:
			cname = input('------------\ncolumn name:\n')
			if cname == 'exit':
				break
			ctype = input('------------\n'+cname+' datatype:\n(integer, decimal or varchar(max_length))\n')
			cselection = input('------------\n'+cname+'\ndo you want to add select option (y/n)\n')
			if cselection == 'y':
				cselection = input("------------\n"+cname+' example:\n{"1":"option1","2":"option2"}\n')
				add.append((cname, ctype, "'{0}'".format(cselection)))
			else:
				add.append((cname, ctype, 'NULL'))
			exit = input('Do you want add another? (y/n)\n')
			if exit != 'y': break
		if len(add) > 0:
			for col in add:
				if type(col) == tuple:
					self.__add(col[0], col[1], col[2])
				else:
					self.__add(col[0], 'varchar ( 50 )', 'NULL')

	def __createEncM(self):
		matrix = []
		order = np.arange(20)
		np.random.shuffle(order)
		for i in order:
			base = np.arange(10)
			np.random.shuffle(base)
			matrix.append([i,list(base)])
			del(base)
		return matrix

	def __testEncM(self, inputEncM):
		try:
			matrix = json.loads(inputEncM)
		except:
			print('input format was wrong')
			return None
		if type(matrix) == list:
			if self.__testEncryption(matrix):
				return matrix
			else:
				return None
		else:
			print('input format was wrong')
			return None

	def __testEncryption(self, encM):
		try:
			urange = range(len(encM))
			code = ['1' for i in urange]
			ecode = ['*' for i in urange]
			for i in urange:	
				ecode[encM[i][0]] = str(encM[i][1][int(code[i])])
			if ''.join(ecode).find('*') >= 0: return False
		except:
			return False
		return True

	def __encMatrix(self, inputEncM):
		if inputEncM == '':
			matrix = self.__createEncM()
		else:
			matrix = self.__testEncM(inputEncM)
		return str(matrix)
			
	def setSettings(self):
		print('set your settings\n')
		addP = 'INSERT INTO settings (name, value) VALUES ("{0}", "{1}");'
		add = []
		printer_id = input('- printer id address:\t\t')
		add.append(addP.format('printer_id',printer_id))
		printer_port = input('- printer port:\t\t\t')
		add.append(addP.format('printer_port',printer_port))
		update_login = input('- update login:\t\t\t')
		add.append(addP.format('update_login',update_login))
		update_pass = getpass.getpass(prompt='- update password:\t\t', stream=None)
		add.append(addP.format('update_pass',update_pass))
		login_link = input('- login link:\t\t\t')
		add.append(addP.format('login_link',login_link))
		update_link = input('- update link:\t\t\t')
		add.append(addP.format('update_link',update_link))
		inputEncM = input('- insert matrix for encryption:\n  -example:[[1,[0,1]],[0,[1,0]]] => code:10->ecode:00\n\t\t\t\t')
		encmatrix = self.__encMatrix(inputEncM)
		add.append(addP.format('encmatrix',encmatrix))
		key_add = input('- key for add or edit function:\t')
		add.append(addP.format('key_addoredit',key_add))
		key_update = input('- key for update function:\t')
		add.append(addP.format('key_update',key_update))
		key_quantity = input('- key for insert quantity:\t')
		add.append(addP.format('key_quantity',key_quantity))
		key_calibration = input('- key for run calibration:\t')
		add.append(addP.format('key_calibration',key_calibration))
		key_language = input('- key for change language:\t')
		add.append(addP.format('key_language',key_language))
		languages = input('- array of languages:\t\t')
		add.append(addP.format('languages',languages))
		#add to database
		self.__write('DELETE FROM settings;')
		for a in add:
			self.__write(a)

	def addLabel(self):
		languages = json.loads(self.__read("SELECT value FROM settings WHERE name='languages'")[0][0].replace("'",'"'))
		select_option = [str(i)+'-'+l for i, l in zip(range(len(languages)),languages)]
		select_language = input('select one language:\n'+'\n'.join(select_option)+'\n\toption: ')
		language = languages[int(select_language)]
		label_name = input('insert label name:\n\t')
		text_editor = input('insert name of text editor: (default vi)\n\t')
		with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8') as tmp:
			if text_editor == '': text_editor = 'vi'
			subprocess.run(text_editor+" "+tmp.name, shell=True, check=True)
			zpl = open(tmp.name,'r', encoding='utf-8').read()
			tmp.flush()
		if len(zpl) != 0:
			self.__write('INSERT INTO label (name, language, zpl) VALUES ("{0}","{1}","{2}")'.format(label_name, language, zpl))
			print('label was add')
		




