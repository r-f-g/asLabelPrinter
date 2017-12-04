# auto scan label printer

The main goal is easy way to printing labels, just by scan EAN code. Program can edit and print label in zpl code on network printer.

## Database structure
#### settings table
- printer id
- used printer port
- login name for online database
	- if it's empty the update function will be not used
- login password
- login link
- update link for download database and send each added product
	- example of receive data:

	```
	{
		'header':
			['EAN','code','ecode',...],
		'data': {
			1:[123,'1000080','2999939',...],
			2:[124,'1000160','2999989',...]
			}
	}
	```
	
	- example of send data:

	```
	{
		'id':1,
		'EAN':123,
		'code':'1000080',
		'ecode':'2999939',
		...
	}
	```
- encmatrix, it's matrix for product code encryption
	- the encrypted code will be stored as "ecode"
	- default matrix will be of size twenty
	- it will be automatically encrypt code of each new product
	- it is good if you want to minimize the chance that the customer finds the product on the Internet
- keyboard shortcut for add new product
- keyboard shortcut for update the database from online service
- keyboard shortcut for calibration printer sensors
- keyboard shortcut for for print more than one labels
 	- example: keyboard shortcut is set up as "q" then 10q123456 will print 10 labels of product with ean code 123456
- keyboard shortcut for change labels language
	- need set up language array (['language1', 'language2'], example: ['SK','HU'])
	- if key will be pressed the language will change

	
#### label table
- name of label
- language of label
- zpl code with modifiable parameter
	- $code$ in zpl code will be change to product code 


#### selection table
- name of specific parameter (column in data table) add by user
- type of parameter (integer, decimal number or string)
- selection text, which will be used when product add or edit
	- example: {"1":"bannan","2":"apple"}
	- if input is 1, than parameter for this product will be set as "banana"
	- it's important if you do not use full keyboard, but just number keyboard

#### data table
- `EAN` EAN code it's not primary key
	- each ENA code can have more labels
- `code` code of each product
- `ecode` encrypted code (if code is number)
- `label` name of label used for product

## Command
`python3 manage.py init` is't for initials database and set up settings

`python3 manage.py setting` command for change settings

`python3 manage.py addColumn` add column (parameter) to data table and it's possible to add selection option for this parameter

`python3 manage.py addLabel` add label to data label table (insert zpl code)

`python3 manage.py run` run auto scan (write exit for quit)

## Example
```
python3 manage.py init
set your settings

- printer id address:		10.1.1.2
- printer port:				9100
- update login:				test
- update password:		
- login link:				http://test.com/login
- update link:				http://test.com/labelprinter
- insert matrix for encryption:
  -example:[[1,[0,1]],[0,[1,0]]] => code:10->ecode:00
				
- key for add or edit function:		* 
- key for update function:			**
- key for insert quantity:			-
- key for run calibration:			++
- key for change language:			/
- array of languages:				['SK','EN']  
```
Encryption matrix was not inserted, but was automatically created for the max length of the code set as 20. This example shows example used for the scanner and numeric keypad.

```
python3 manage.py addColumn
------------
column name:
capacity
------------
capacity datatype:
(integer, decimal or varchar(max_length))
varchar(20)
------------
capacity
do you want to add select option (y/n)
y
------------
capacity example:
{"1":"option1","2":"option2"}
{"1":"80GB","2":"160GB","3":"320GB","4":"500GB","5":"1TB"}
Do you want add another? (y/n)
n
capacity was added successfully
```
Insert parameter with select option.

```
python3 manage.py addLabel
select one language:
0-SK
1-EN
	option: 1
insert label name:
	hdd
insert name of text editor: (default vi)
	nano
label was add
```
With nano we add zpl code.

```
^XA

^FX Top section with company logo, name and address.
^CF0,60
^FO50,50^GB100,100,100^FS
^FO75,75^FR^GB100,100,100^FS
^FO88,88^GB50,50,50^FS
^FO180,100^FDHDD $capacity$^FS
^CF0,40

^FX Third section with barcode.
^BY5,2,180
^FO10,200^BC^FD$code$^FS

^XZ
```
Last thing is add product to data table, what we can do with running script.

```
python3 manage.py run

---start scanning

SK:/
EN:123

ERR102 - EAN 123 is not in database

EN:*

---add or edit---

EAN:
123
--select--
0-hdd
----------
0
code:
1000080   
used ecode:
9965876
select capacity
--select--
0-
1:80GB
2:160GB
3:320GB
4:500GB
5:1TB
----------
1
--done--
EN:123
```
The result of this is printed label on network printer with ip address 10.1.1.2.

![](label.png)

