# asLabelPrinter

The main goal is easy way to printing labels just by scan EAN code. Program can edit and print labes in zpl code on network printer.

## Database structure
#### settings table
- printer id
- used printer port
- login name for online database
	- if it's empty the update function will be not use
- login password
- login link
- update link for download database and sed all add product
	- example of recive data:
	- example of send data:
- encmatrix, it's matrix for product code encryption
	- the encrypted code will be store as "ecode"
	- defualt matrix will be of size twenty
	- it will be automaticaly encrypt code of all new product
	- it's good if you want to minimize change that you customer find product online
	- example:
- key for add new product
- key for update database from online service
- key for for prit more than one labels
 	- example: key is set up as "q" than 10q123456 will print 10 labels of product with ean code 123456
- key for change language of labes
	- need set up language array (['language1', 'language2'], example: ['SK','HU'])
	- if key will be pressed the language will change

	
#### labe table
- name of label
- language of label
- zpl code with modifiable parameter
	- $code$ in zpl code will be change to product code 


#### selection table
- name of specific parameter (column in table data) add by user
- type of parameter (integer, deciaml number or string)
- selection text, which will bw used when product add or edit
	- example: {"1":"bannan","2":"apple"}
	- if input is 1, than parapeter for this product will be set as "banna"
	- it's important if you do not used full keyboard, but just number keyboard

#### data table
- ean code it's not primary key
	- one ean cen have more labels
- code of each product
- encrypted code
- name of label used for product

## Comand
asdasd