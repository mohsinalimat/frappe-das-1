import frappe
from frappe.utils import get_request_session
import json

def send_notification_gilang(auth_key,data):
	try:
		s = get_request_session()
		url = "https://fcm.googleapis.com/fcm/send"

		# user = frappe.get_doc("User",user)
		
		# frappe_userid = user.social_logins[0].userid + "_android"
		frappe_userid = "767f244ce59f92203916b735a442a643b9a6df0"+"_android"

		header = {"Authorization": "key={}".format(auth_key),"Content-Type": "application/json"}
		content = {
			"to":"/topics/{}".format(frappe_userid),
			"data":data
		}
		res = s.post(url=url,headers=header,data=json.dumps(content))
		return res
	except:
		return "Error"


# def send_notification_global_android(auth_key,data):
# 	try:
# 		s = get_request_session()
# 		url = "https://fcm.googleapis.com/fcm/send"	
# 		header = {"Authorization": "key={}".format(auth_key),"Content-Type": "application/json"}
# 		content = {
# 			"to":"/topics/all_android",
# 			"data":data
# 		}
# 		res = s.post(url=url,headers=header,data=json.dumps(content))
# 		return res
# 	except:
# 		return "Error"

# def send_notification_global_ios(auth_key,title,body):
# 	try: 
# 		s = get_request_session()
# 		url = "https://fcm.googleapis.com/fcm/send"
# 		header = {"Authorization": "key={}".format(auth_key),"Content-Type": "application/json"}
# 		content = {
# 			"to":"/topics/all_ios",
# 			"notification":{
# 				"body":body,
# 				"title":title
# 			}
# 		}
# 		res = s.post(url=url,headers=header,data=json.dumps(content))
# 		return res
# 	except:
# 		return "Error"

# def send_notification_global_ios_image(auth_key,title,body,image):
# 	try:
# 		s = get_request_session()
# 		url = "https://fcm.googleapis.com/fcm/send"

# 		header = {"Authorization": "key={}".format(auth_key),"Content-Type": "application/json"}
# 		content = {
# 			"to":"/topics/all_ios",
# 			"content_available": True,
# 			"priority" : "high",
# 			"data":{
# 				"body":body,
# 				"title":title,
# 				"mutable_content":True,
# 				"image": image,
# 				"sound": "default"
# 			}
# 		}
# 		res = s.post(url=url,headers=header,data=json.dumps(content))
# 		return res
# 	except:
# 		return "Error"

def send_notification_android(user,auth_key,data):
	try:
		s = get_request_session()
		url = "https://fcm.googleapis.com/fcm/send"

		user = frappe.get_doc("User",user)
		
		if (len(user.social_logins) > 0):
			frappe_userid = user.social_logins[0].userid + "_android"

			header = {"Authorization": "key={}".format(auth_key),"Content-Type": "application/json"}
			content = {
				"to":"/topics/{}".format(frappe_userid),
				"data":data
			}
			res = s.post(url=url,headers=header,data=json.dumps(content))
			print(res)
			return res
	except:
		return "Error"

def send_notification_ios(user,auth_key,title,body):
	try:
		s = get_request_session()
		url = "https://fcm.googleapis.com/fcm/send"

		user = frappe.get_doc("User",user)
		
		if (len(user.social_logins) > 0):
			print(user.name)
			frappe_userid = user.social_logins[0].userid + "_ios"

			header = {"Authorization": "key={}".format(auth_key),"Content-Type": "application/json"}
			content = {
				"to":"/topics/{}".format(frappe_userid),
				"notification":{
				"body":body,
				"title":title,
				"sound": "default"
				},
				"priority": "high"
			}
			res = s.post(url=url,headers=header,data=json.dumps(content))
			print(content)

			print(res)
			return res
	except:
		return "Error"


def send_notification_by_mobile_no(mobile_no,auth_key,data):
	try:
		s = get_request_session()
		url = "https://fcm.googleapis.com/fcm/send"
		
		header = {"Authorization": "key={}".format(auth_key),"Content-Type": "application/json"}
		content = {
			"to":"/topics/{}".format(mobile_no),
			"data":data
		}
		res = s.post(url=url,headers=header,data=json.dumps(content))
	except:
		return "Error"
		
# # testing image ios

def send_notification_ios_image(user,auth_key,title,body,image):
	try:
		s = get_request_session()
		url = "https://fcm.googleapis.com/fcm/send"

		user = frappe.get_doc("User",user)
		
		if (len(user.social_logins) > 0):
			frappe_userid = user.social_logins[0].userid + "_ios"

			header = {"Authorization": "key={}".format(auth_key),"Content-Type": "application/json"}
			content = {
				"to":"/topics/{}".format(frappe_userid),
				"content_available": True,
				"priority" : "high",
				"data":{
					"body":body,
					"title":title,
					"mutable_content":True,
					"image": image,
					"sound": "default"
				}
			}
			res = s.post(url=url,headers=header,data=json.dumps(content))
			print(res)
			return res
	except:
		return "Error"