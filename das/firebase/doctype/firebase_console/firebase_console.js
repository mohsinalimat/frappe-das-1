// Copyright (c) 2019, digitalasiasolusindo@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Firebase Console', {
	refresh: function(frm) {

	},
	user: function(frm) {
		frappe.call({
		    method: 'das.firebase.topic.get_topic',
		    args: {
		    	'user': frm.doc.user
		    },
		    callback: function(r) {
		    	console.log(r)
		        if (r.message != null) {
		        	var topic = r.message.data.topic
		        	frm.set_value("topic",topic)
		        }
		    }
		});
	}
});
