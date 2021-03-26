# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
	'name': 'Delivery Order after Sale Confirm',
	'version': '13.0.1.1', 
	'licence': 'Other proprietary',
	'sequence': 1, 
	'category': 'Sales', 
	'description': '''In odoo, sometime when confirm sale order and process partial delivery order without back order then there is no option to create new delivery order and link to same sale order so for the solution odoo app generate delivery order after sale order confirm will allow you to create a delivery order.

1.Create Delivery order after sale order confirm in single click for reaming delivered quantity .

 odoo application will help to create delivery order after sale order confirm.
        
        odoo delivery order
        odoo sale confrim delivery order 
        odoo sale delivery order 
        generate delivery after sale confirm
        delivery with no back order

odoo app to create a delivery order after-sale order confirmation, sale after delivery, a delivery order from sale, sale to delivery, redelivery sale order, after confirming sale delivery  order, recreate delivery order, generate delivery after sale confirm, delivery with no back order
''', 
	'summary': '''odoo app to create a delivery order after-sale order confirmation, sale after delivery, a delivery order from sale, sale to delivery, redelivery sale order, after confirming sale delivery  order, recreate delivery order, generate delivery after sale confirm, delivery with no back order''', 
	'depends': ['sale_stock', 'stock'],
	'data': [
		'wizard/delivery_create_wizard_views.xml'],
	'demo': [],
	'test': [],
	'css': [],
	'qweb': [],
	'js': [],
	'images': [
		'images/main_screenshot.png'],
	'installable': True, 
	'application': True, 
	'auto_install': False, 
	#========= Author and Support Details =========#
	'author': 'DevIntelle Consulting Service Pvt.Ltd', 
	'website': 'http://www.devintellecs.com', 
	'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
	'support': 'devintelle@gmail.com', 
	'price': 25.0, 
	'currency': 'EUR', 
	'live_test_url': 'https://youtu.be/oahewaDJ0LY', 

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: