import frappe
import sys
import json

def success_format(doc):
	data = dict()
	data['code'] = 200
	data['data'] = doc
	return data

def error_format(err):
	data = dict()
	data['code'] = 500
	data['error'] = str(err).replace("ValidationError(u'","").replace("',)","").replace('ValidationError(u"','",)')
	return data 

@frappe.whitelist(allow_guest=True)
def test_validation():
	try:
		frappe.throw("baca aku")
	except:
		return error_format(sys.exc_info()[0])

@frappe.whitelist(allow_guest=False)
def validate_get_list(doctype):
	try:
		tryFetch = frappe.get_list(doctype)
		return success_format("success")
	except:
		return error_format(sys.exc_info()[0])


@frappe.whitelist(allow_guest=False)
def insert_doctype():
	try:
		data = json.loads(frappe.form_dict.data)
		doc = frappe.get_doc(data)
		doc.insert()
		return success_format(doc)
	except:
		return error_format(sys.exc_info()[0])

