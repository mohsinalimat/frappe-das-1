import frappe
from validation import *
from frappe.auth import check_password
from file_manager import upload
import sys
import hashlib
import json
import time

VERSION = "1.1"
@frappe.whitelist(allow_guest=True)
def version():
	return VERSION

@frappe.whitelist(allow_guest=False)
def get_list(doctype,filters='',fields='*',limit=20,page=0,order_by="modified DESC"):
	try:
		resource = frappe.get_list(doctype,
						fields=fields,
						filters=filters,
						limit_page_length=limit,
						limit_start=page,
						order_by=order_by)
		return success_format(resource)
	except:
		return error_format(sys.exc_info()[1])


@frappe.whitelist(allow_guest=False)
def get_doc(doctype,name):
	try:
		resource = frappe.get_doc(doctype, name)
		return success_format(resource)
	except:
		return error_format(sys.exc_info()[1])


@frappe.whitelist(allow_guest=True)
def test_json():
	for header in frappe.request.headers:
		if header[0] == "Token":	
			return header[1]
	
	

@frappe.whitelist(allow_guest=False)
def update(doctype,name):
	try:
		data = json.loads(frappe.form_dict.data)
		doc = frappe.get_doc(doctype,name)
		doc.update(data)
		doc.save()
		frappe.db.commit()
		return success_format(doc)
	except:
		return error_format(sys.exc_info()[1])

@frappe.whitelist(allow_guest=False)
def delete(doctype,name):
	try:
		doc = frappe.delete_doc(doctype,name)
		frappe.db.commit()
		return success_format(doc)
	except:
		return error_format(sys.exc_info()[1])

@frappe.whitelist(allow_guest=False)
def insert():
	try:
		data = json.loads(frappe.form_dict.data)
		doc = frappe.get_doc(data)
		doc.insert()
		frappe.db.commit()
		return success_format(doc)
	except:
		return error_format(sys.exc_info()[1])

@frappe.whitelist(allow_guest=False)
def change_password():
	if frappe.request.data is None: 
		return "Forbidden"
	
	data = json.loads(frappe.request.data)

	email = frappe.session.user
	data_user = frappe.db.sql("SELECT name FROM `tabUser` WHERE name='{}'".format(email),as_dict=True)

	if (len(data_user) > 0):
		try:
			check_password(data_user[0]['name'],data['old_pwd'])
		except frappe.AuthenticationError:
			return error_format('old password is incorrect')

		new_user = {
			"new_password":data['new_pwd']
		}

		doc = frappe.get_doc("User",data_user[0]['name'])
		doc.flags.ignore_permissions = True
		doc.update(new_user)
		doc.save()
		frappe.db.commit()

		return success_format(doc)
	return error_format(sys.exc_info())


@frappe.whitelist(allow_guest=True)
def attach_file():
	response = {}

	req = frappe.local.form_dict

	hash = hashlib.sha1()
	hash.update(str(time.time()))
	hash_now = hash.hexdigest()[:10]

	data = json.loads(req.data)
	req.filename = "attachment_{}_{}".format(hash_now,data['filename'])

	req.filedata = data['filedata']
	req.name = data['name']

	try:

		uploaded = upload(data['doctype'],req.name,1)

		response["code"] = 200
		response["message"] = "Success"
		response["data"] = uploaded

	except Exception as e:
		response["code"] = 400
		response["message"] = e.message
		response["data"] = ""
	except UnboundLocalError as e:
		response["code"] = 400
		response["message"] = e.message
		response["data"] = ""

	return response

