from frappe import _

def get_data():
	return {
		'transactions': [
			{
				'label': _('Console'),
				'items': ['Firebase Console']
			},
			{
				'label': _('Log'),
				'items': ['Firebase Log']
			},
		]
	}
