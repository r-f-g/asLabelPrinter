import sqlite3, json, os, sys, socket, time
import requests

class scan:
	def __init__(self):
		self.database_name = 'database.sqlite3'
		if os.path.exists(self.database_name) == False:
			sys.tracebacklimit = None
			raise NameError('the database was not initialized')
		self.settings = {s[0]:s[1] for s in self.__read('SELECT name, value FROM settings;')}
		self.settings['languages'] = json.loads(self.settings['languages'].replace("'",'"'))
		self.settings['encmatrix'] = json.loads(self.settings['encmatrix'])
		self.columns = {s[0]:{'type':s[1], 'value':s[2]} for s in self.__read('SELECT name, type, value FROM selection;')}
		self.labels = {l[0]:{'name':l[1], 'zpl':l[2]} for l in self.__read('SELECT id, name, language, zpl FROM label;')}
		self.labelsName = {str(i):l[0] for i,l in enumerate(self.__read('SELECT DISTINCT name FROM label;'))}
		self.language = 0

	def __eprint(self, zpl, quantity):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((self.settings['printer_id'], int(self.settings['printer_port'])))
			for i in range(quantity):
				s.send(bytes(zpl, "utf-8"))
				time.sleep(0.05)
			s.close()
		except:
			print('\nERR002 - problem with printer\n')

	def __read(self, sql, name=False):
		conn = sqlite3.connect(self.database_name)
		c = conn.cursor()
		c.execute(sql)
		header = {d[0]:i for i,d in enumerate(c.description)}
		data = c.fetchall()
		conn.commit()
		conn.close()
		if name: return data, header
		return data

	def __write(self, sql):
		conn = sqlite3.connect(self.database_name)
		c = conn.cursor()
		c.execute(sql)
		id = c.lastrowid
		conn.commit()
		conn.close()
		return id

	def __test(self, inp):
		if inp == 'exit':
			return True
		elif inp == self.settings['key_addoredit']:
			self.__addORedit()
		elif inp == self.settings['key_update']:
			if self.settings['update_login'] != None: self.__update()
		elif inp == self.settings['key_language']:
			self.__language()
		else:
			quantity, ean = self.__quantity(inp)
			if ean == 0: return False
			zpl = self.__getZPL(ean)
			if zpl != None: self.__eprint(zpl, quantity)
		return False

	def __encryption(self, code):
		if self.settings['encmatrix'] == None: return None
		try:
			h0 = [' ' for i in range(len(self.settings['encmatrix']))]
			for i in range(len(code)):
				h0[self.settings['encmatrix'][i][0]] = str(self.settings['encmatrix'][i][1][int(code[i])])
			ecode = (''.join(h0)).replace(' ','')
			return ecode
		except:
			return None

	def __selection(self, selection, option=None):
		if option == None:
			option = '0-\n'+selection.replace('"','').replace("'",'').replace('{','').replace('}','').replace(',','\n')
			try:
				selection = json.loads(selection.replace("'",'"'))
				selection['0'] = None
			except:
				return None
		select = input('--select--\n'+option+'\n----------\n')
		try:
			return selection[select]
		except:
			print('wrong selection')
			return self.__selection(selection, option)

	def __format(self, data, datatype):
		if data == None or data == '': return 'NULL'
		if datatype == 'int':
			return "{0}".format(int(data))
		if datatype == 'dec':
			return "{0}".format(float(data.replace(',','.')))
		elif datatype == 'str':
			return '"{0}"'.format(data)
		else:
			return 'NULL'

	def __editValue(self):
		values = {}
		values['code'] = input('code:\n')
		values['ecode'] = self.__encryption(values['code'])
		print('used ecode:\n{0}'.format(values['ecode']))
		for col in self.columns:
			if self.columns[col]['value'] == None:
				values[col] = self.__format(input('column {0}:\n'.format(col)), self.columns[col]['type'])
			else:
				print('select '+col)
				values[col] = self.__format(self.__selection(self.columns[col]['value']), self.columns[col]['type'])
		return values

	def __inputINT(self, name):
		try:
			return int(input(name+':\n'))
		except:
			print("It's not integer!!!")
			return self.__inputINT(name)

	def __existsEAN(self, EAN):
		data = self.__read('SELECT id,code FROM data WHERE EAN={0}'.format(EAN))
		n = len(data)
		if n == 0:
			return 0
		else:
			option = input('EAN:{0} exists in database.\nDo you want to edit it or add new? (e|1 / a|2 / n|3)\n'.format(EAN))
			if option == 'e' or option == '1':
				if n > 1:
					row = self.__selection({str(i):data[i] for i in range(n)}, '\n'.join(['{0}-{1}'.format(i,data[i][1]) for i in range(n)]))
				else:
					row = data[0]
				return row[0]
			elif option == 'a' or option == '2':
				return 0
			else:
				return -1

	def __send(self, id):
		print('--send--\nconecting...')
		client = requests.session()
		client.get(self.settings['login_link'])
		login_data = {'username':self.settings['update_login'],'password':self.settings['update_pass'], 'csrfmiddlewaretoken':client.cookies['csrftoken']}
		r1=client.post(self.settings['login_link'], data=login_data)
		if r1.text.find('Zadali ste zle meno alebo heslo. Prosím skúste to znova.') >= 0:
			print('\nERR401 - problem with login to online service\n')
			return
		print('successful login')
		try:
			select, header = self.__read('SELECT * FROM data WHERE id={0};'.format(id), True)
			data = {h:select[0][header[h]] for h in header}
		except:
			print('\nERR402 - problem with get data\n')
		try:
			r2=client.post(self.settings['update_link']+'add', data={'csrfmiddlewaretoken':client.cookies['csrftoken'], 'data':json.dumps(data)})
			print(r2.json()['message'])
		except:
			print('\nERR403 - problem with send data to online service\n')
		print('--done--')
		client.close()

	def __addORedit(self):
		print('\n---add or edit---\n')
		EAN = self.__inputINT('EAN')
		edit = self.__existsEAN(EAN)
		if edit == -1: return 
		label = self.__selection(self.labelsName, '\n'.join(['{0}-{1}'.format(l,self.labelsName[l]) for l in self.labelsName]))
		try:
			values = self.__editValue()
		except:
			print('\nERR202 - problem with edit values\n')
			return
		col, val = ['`EAN`','`label`'], [str(EAN), '"{}"'.format(label)]
		for c in values:
			col.append('`{0}`'.format(c))
			if values[c] == '' or values[c] == None:
				val.append('NULL')
			else:
				val.append(values[c])
		try:
			if edit == 0:
				id = self.__write('INSERT INTO data ({0}) VALUES ({1});'.format(','.join(col), ','.join(val)))
			else:
				id = edit
				update = ['{0}={1}'.format(c, v) for c, v in zip(col, val)]
				self.__write('UPDATE data SET {0} WHERE id={1};'.format(','.join(update), id))
		except:
			print('\nERR201 - problem with writing to database\n')
		try:
			if self.settings['update_login'] != None: self.__send(id)
		except:
			print('\nERR203 - problem with send change\n')
		print('--done--')

	def __getFormat(self, column):
		try:
			return "{0}".format(int(column))
		except:
			pass
		try:
			return "{0}".format(float(column))
		except:
			pass
		try:
			return "'{0}'".format(column)
		except:
			pass
		return 'NULL'

	def __update(self):
		print('---update---\nconecting...')
		client = requests.session()
		client.get(self.settings['login_link'])
		login_data = {'username':self.settings['update_login'],'password':self.settings['update_pass'], 'csrfmiddlewaretoken':client.cookies['csrftoken']}
		r1=client.post(self.settings['login_link'], data=login_data)
		if r1.text.find('Zadali ste zle meno alebo heslo. Prosím skúste to znova.') >= 0:
			print('\nERR301 - problem with login to online service\n')
			return
		print('successful login')
		r2=client.get(self.settings['update_link']+'load', data={'csrfmiddlewaretoken':client.cookies['csrftoken']})
		client.close()
		try:
			if r2.json()['status'] == 'ok':
				data = r2.json()['data']['data']
				header = ','.join(r2.json()['data']['header'])
				print('all data was recive')
			else:
				print('online service message'+r2.json()['message'])
				return
		except:
			print('\nERR302 - problem read data from online service\n')
			return
		try:
			sql = 'INSERT OR REPLACE INTO data (id, {0}) VALUES ({1})'
			for d in data:
				row = [str(d)]
				for c in data[d]:
					if c == "" or c == 'null' or c == None:
						row.append('NULL')
					else:
						row.append(self.__getFormat(c))
				self.__write(sql.format(header, ','.join(row)))
		except:
			print('\nERR303 - problem with write data from online service\n')
			return

	def __language(self):
		self.language += 1
		if self.language >= len(self.settings['languages']):
			self.language = 0

	def __quantity(self, inp):
		try:
			h0 = inp.find(self.settings['key_quantity'])
			quantity = 1 if h0 == -1 else int(inp[:h0])
			ean = int(inp[h0+1:])
			return quantity, ean
		except:
			print('\nERR101 - problem with EAN or quantity\n')
			return 0, 0

	def __chooseOne(self, data, text):
		if len(data) == 1: return data[0]
		try:
			return data[int(input(text))]
		except:
			return self.__chooseOne(data, text)

	def __getSelectOption(self, data, header):
		out = ''
		for i,d in enumerate(data):
			out += '{1}-{0}\n'.format(d[header['code']],i)
		return out

	def __editZPL(self, zpl, row, header):
		try:
			for h in header:
				zpl = zpl.replace('${0}$'.format(h), str(row[header[h]]) if row[header[h]] != None else '')
			return zpl
		except Exception as e:
			print('\nERR104 - problem with edit zpl code'+str(e))
			return None

	def __getZPL(self, ean):
		data, header = self.__read('SELECT * FROM data WHERE EAN={0};'.format(ean), True)
		if data == []:
			print('\nERR102 - EAN {0} is not in database\n'.format(ean))
			return None
		row = self.__chooseOne(data, self.__getSelectOption(data, header))
		try:
			zpl = self.__read('SELECT zpl FROM label WHERE name="{0}" AND language="{1}";'.format(row[header['label']], self.settings['languages'][self.language]))[0][0]
		except:
			print('\nERR103 - label {0}_{1} is not in database\n'.format(row[header['label']], self.settings['languages'][self.language]))
			return None
		zpl = self.__editZPL(zpl, row, header)
		return zpl

	def __scan(self):
		try:
			return input(self.settings['languages'][self.language]+':')
		except:
			print('ops something is wrong...')
			return None

	def run(self):
		print('\n---start scanning\n')
		try:
			while True:
				inp = self.__scan()
				if self.__test(inp): break
		except:
			print('\nERR001\n')
			return True
		print('\n---stop scanning\n')
		return False