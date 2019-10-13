import frappe
import string
from random import *
from das.helper import *

def after_insert(self, method):
	try:
		# frappe.msgprint(self.file_url+" dan "+self.attached_to_doctype+" dan "+self.attached_to_name)
		# filesname = "files/" + self.name
		if "thumbnail" not in self.file_url:
			generate_thumbnail(self.file_url,self.attached_to_doctype,self.attached_to_name)
		print("oke")
		# frappe.msgprint(self.attached_to_doctype)
		# frappe.msgprint(self.attached_to_name)
		# frappe.msgprint(self.file_url)
		# frappe.msgprint(self.file_size)
	except:
		# frappe.msgprint(self.file_url)
		print("error")

#helper function and must be tested
def find_doc_thumbnail(file_name):
	return frappe.get_value("File",{"file_name": "thumbnail_{}".format(file_name)}, "name")

# def delete_attachment(doctype, name)

def after_delete(self, method):
	try:
		# find file doc with filename with thumbnail_
		thumbnail_doc = find_doc_thumbnail(self.file_name)
		frappe.delete_doc("File", thumbnail_doc)
		frappe.db.commit()

	except:
		print("error  when deleting file")