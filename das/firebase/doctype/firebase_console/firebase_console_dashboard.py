from frappe import _

def get_data():
	return {
		'transactions': [
			{
				'label': _('Setting'),
				'items': ['Firebase Setting']
			},
			{
				'label': _('Log'),
				'items': ['Firebase Log']
			},
		]
	}
