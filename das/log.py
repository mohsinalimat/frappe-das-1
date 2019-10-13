import frappe

def global_log(title="", document="", name="", url="", response_code="", payload="", response="", error_type=""):
    doc = frappe.get_doc({
        'doctype':"Global Log",
        'title': title,
        'document':document,
        'log_name':name,
        'url':url,
        'response_code':response_code,
        'payload':payload,
        'response':response,
        'error_type':error_type
    })
    doc.save(ignore_permissions=True)
    frappe.db.commit()