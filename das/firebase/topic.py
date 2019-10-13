import frappe
from das.validation import *


def _get_topic(user):
	user_doc = frappe.get_doc("User",user)
	frappe_userid = ""
	if (len(user_doc.social_logins) > 0):
			frappe_userid = user_doc.social_logins[0].userid

	return frappe_userid

@frappe.whitelist()
def get_topic(user):
	user_doc = frappe.get_doc("User",user)
	frappe_userid = ""
	if (len(user_doc.social_logins) > 0):
			frappe_userid = user_doc.social_logins[0].userid

	return success_format({
			"topic" : frappe_userid,
			"ios" : str(frappe_userid) + "_ios",
			"android" : str(frappe_userid) + "_android"
		})
