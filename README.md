# Frappe DAS Library

Frappe DAS is a open-source library to enhance your framework on Frappe Framework including:
- Firebase Integration


### Firebase Integration

###### Requirement:
  - Google Firebase Console Account


###### Setup on Frappe:
  - Setup on Firebase Setting (Your Project Name, URL, and Server Key)
  - Subscribe your Android/iOS Device using Frappe UserID
  - Try it on Firebase Console
  
###### Client-side (iOS/Android):
  - Get topic corresponding to User
  - Use topic corresponding to device
  - Subscribe to Firebase on device
```
http://{frappe_instance}/api/method/das.firebase.topic.get_topic?user=<USER>
```
Response:
```json
{
    "message": {
        "code":200,
        "data": {
            "topic": <USER_TOPIC>,
            "ios" : <USER_TOPIC_IOS>,
            "android" : <USER_TOPIC_ANDROID>,
        }
    }
}
```
Server-side:
You can check more documentation file on ```das/firebase/notification.py```
  - Send basic notification (only title and body)
```python
#Public Function: Send notification to iOS and Android Devices
"""
    user:String             -> corresponding to receiver (Link to User)
    title:String             -> title of the notification
    body:String                -> body of the notification
    badge:Int (optional)    -> badge of the notification
"""
send_notification_basic(user,title,body,badge=0)
```
  - Send notification with data
```
#Public Function: Send notification to iOS and Android Devices with data
"""
    user:String             -> corresponding to receiver (Link to User)
    title:String             -> title of the notification
    body:String                -> body of the notification
    data:String                -> data of the notification
    badge:Int (optional)    -> badge of the notification
"""
send_notification_data(user,title,body,data,badge=0)
```


### Installation


Install using bench

```sh
$ bench get-app das https://github.com/davidcast95/frappe-das
$ bench install-app das
```

