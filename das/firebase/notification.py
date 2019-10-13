import frappe
import json

from das.error import error_result
from frappe.utils import get_request_session
from topic import _get_topic
from log import log_notification_success, log_notification_failed

#FCM URL
url = "https://fcm.googleapis.com/fcm/send"

#Private Function: Return Server Key FCM
def get_auth_key():
	return frappe.get_value("Firebase Setting","Firebase Setting","server_key")

#Public Function: Send notification to iOS Devices
"""
	user:String 			-> corresponding to receiver (Link to User)
	title:String 			-> title of the notification
	body:String				-> body of the notification
	badge:Int (optional)	-> badge of the notification
"""
def send_notification_ios(user,title,body,badge=0):

	s = get_request_session()
	auth_key = get_auth_key()

	if auth_key == "":
		frappe.throw("Server key has been not set")
	else:
		frappe_userid = _get_topic(user)

		if frappe_userid != "": 
			header = {"Authorization": "key={}".format(auth_key),"Content-Type": "application/json"}
			topic = "/topics/{}_ios".format(frappe_userid)
			content = {
				"to":topic,
				"notification":{
					"body":body,
					"title":title,
					"badge":badge,
					"sound": "default"
				},
				"priority": "high"
			}
			res = s.post(url=url,headers=header,data=json.dumps(content))

			#logging
			response_code = res.status_code
			if response_code == 200:
				res_json = res.json()
				message_id = res_json["message_id"]
				log_notification_success(response_code,message_id,user,topic,title,body,json.dumps(content),badge)
				frappe.msgprint("iOS Success notified")
			else:
				error = res.text
				log_notification_failed(response_code,user,topic,title,body,error)
				frappe.throw(error)
		else:
			frappe.throw("User not found")


#Public Function: Send notification to Android Devices
"""
	user:String 			-> corresponding to receiver (Link to User)
	title:String 			-> title of the notification
	body:String				-> body of the notification
"""
def send_notification_android(user,title,body):

	s = get_request_session()
	auth_key = get_auth_key()

	if auth_key == "":
		frappe.throw("Server key has been not set")
	else:
		frappe_userid = _get_topic(user)

		if frappe_userid != "": 
			header = {"Authorization": "key={}".format(auth_key),"Content-Type": "application/json"}
			topic = "/topics/{}_android".format(frappe_userid)
			content = {
				"to":topic,
				"notification":{
					"body":body,
					"title":title
				}
			}
			res = s.post(url=url,headers=header,data=json.dumps(content))

			#logging
			response_code = res.status_code
			if response_code == 200:
				res_json = res.json()
				message_id = res_json["message_id"]
				log_notification_success(response_code,message_id,user,topic,title,body,json.dumps(content))
				frappe.msgprint("Android Success notified")
			else:
				error = res.text
				log_notification_failed(response_code,user,topic,title,body,error)
				frappe.throw(error)
		else:
			frappe.throw("User not found")


#Public Function: Send notification to iOS and Android Devices
"""
	user:String 			-> corresponding to receiver (Link to User)
	title:String 			-> title of the notification
	body:String				-> body of the notification
	badge:Int (optional)	-> badge of the notification
"""
def send_notification_basic(user,title,body,badge=0):

	send_notification_ios(user,title,body,badge)
	send_notification_android(user,title,body)


#Public Function: Send notification to iOS Devices with data
"""
	user:String 			-> corresponding to receiver (Link to User)
	title:String 			-> title of the notification
	body:String				-> body of the notification
	data:JsonObject			-> data of the notification
	badge:Int (optional)	-> badge of the notification
"""
def send_notification_data_ios(user,title,body,data,badge=0):

	s = get_request_session()
	auth_key = get_auth_key()

	if auth_key == "":
		frappe.throw("Server key has been not set")
	else:
		frappe_userid = _get_topic(user)

		if frappe_userid != "": 
			header = {"Authorization": "key={}".format(auth_key),"Content-Type": "application/json"}
			topic = "/topics/{}_ios".format(frappe_userid)
			content = {
				"to":topic,
				"notification":{
					"body":body,
					"title":title,
					"badge":badge,
					"mutable_content":True,
					"sound": "default"
				},
				"priority": "high"
			}
			content['notification'].update(data)
			res = s.post(url=url,headers=header,data=json.dumps(content))

			#logging
			response_code = res.status_code
			if response_code == 200:
				res_json = res.json()
				message_id = res_json["message_id"]
				log_notification_success(response_code,message_id,user,topic,title,body,json.dumps(content),json.dumps(data),badge)
				frappe.msgprint("iOS Success notified")
			else:
				error = res.text
				log_notification_failed(response_code,user,topic,title,body,error)
				frappe.throw(error)
		else:
			frappe.throw("User not found")


#Public Function: Send notification to Android Devices with data
"""
	user:String 			-> corresponding to receiver (Link to User)
	title:String 			-> title of the notification
	body:String				-> body of the notification
	data:JsonObject			-> data of the notification
"""
def send_notification_data_android(user,title,body,data):

	s = get_request_session()
	auth_key = get_auth_key()

	if auth_key == "":
		frappe.throw("Server key has been not set")
	else:
		frappe_userid = _get_topic(user)

		if frappe_userid != "": 
			header = {"Authorization": "key={}".format(auth_key),"Content-Type": "application/json"}
			topic = "/topics/{}_android".format(frappe_userid)
			content = {
				"to":topic,
				"data":{
					"body":body,
					"title":title
				}
			}
			content['data'].update(data)
			res = s.post(url=url,headers=header,data=json.dumps(content))

			#logging
			response_code = res.status_code
			if response_code == 200:
				res_json = res.json()
				message_id = res_json["message_id"]
				log_notification_success(response_code,message_id,user,topic,title,body,json.dumps(content),json.dumps(data))
				frappe.msgprint("Android Success notified")
			else:
				error = res.text
				log_notification_failed(response_code,user,topic,title,body,error)
				frappe.throw(error)
		else:
			frappe.throw("User not found")


#Public Function: Send notification to iOS and Android Devices with data
"""
	user:String 			-> corresponding to receiver (Link to User)
	title:String 			-> title of the notification
	body:String				-> body of the notification
	data:String				-> data of the notification
	badge:Int (optional)	-> badge of the notification
"""
def send_notification_data(user,title,body,data,badge=0):

	#check data json format
	try:
		data_json = json.loads(data)
	except: 
		frappe.throw(error_result())

	send_notification_data_ios(user,title,body,data_json,badge)
	send_notification_data_android(user,title,body,data_json)


	