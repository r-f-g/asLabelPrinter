import sys, time
from modul import database
from modul import autoScan

help_note = '''
init -			initialize database
addColumn -		insert columns to 'data' table
settings -		edit settings
addLabel -		add new labels
run -			run scaning
			'''

def main(option):
	if option == 'help':
		print(help_note)
	elif option == 'init':
		d = database.database()
		init = d.init()
		if init: d.setSettings()
	elif option == 'addColumn':
		d = database.database()
		d.addColumn()
	elif option == 'settings':
		d = database.database()
		d.setSettings()
	elif option == 'addLabel':
		d = database.database()
		d.addLabel()
	elif option == 'run':
		a = autoScan.scan()
		if a.run():
			time.sleep(2)
			main(option)
	else:
		print(help_note)

if __name__ == "__main__":
	try:
		option = sys.argv[1]
	except:
		print('"manage.py help" to see option')
	main(option)