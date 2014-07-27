# Need function to generate dictionary

import datetime as dt

dummy_data = {'ids': [{'type': '', 'id': '000', 'name': '', 'delete':True}, 
			{'in_cats': [], 'deleted': False, 'type': 'task', 'id': '001', 'name': 'First Task'}, 
			{'in_cats': [], 'deleted': False, 'type': 'task', 'id': '002', 'name': 'Second Task'}, 
			{'in_cats': [], 'deleted': True, 'type': 'task', 'id': '003', 'name': 'Third Task'}, 
			{'in_cats': [], 'deleted': False, 'type': 'task', 'id': '004', 'name': 'Fourth Task'}], 
			'entries': [{'id':'000', 'task_id': ''}]}

def get_tasks_cat(data, cat):
	"""Gets tasks for sepcified category"""
	pass

def get_cats_task(data, tasks):
	"""Gets categories for specified task."""
	pass

def get_task_name(data, task_id):
	"""Get name of task from dictionary using id. If no task exists return False."""
	for d in data:
		# print d['id']
		if task_id==d['id']:
			return d['name'] 
	return False

def list_all_tasks(data):
	"""Return list of dictionaries which contain undeleted tasks."""
	return [d for d in data if (d['type']=='task' and not d['deleted'])]


def list_all_cats(data):
	"""Returns a list with all the categories."""
	return [d['name'] for d in data if d['type']=='cat']

def add_task(data, new_task):
	"""Adds a new task."""
	new_id = data[-1]['id'] + 1 if data else 0
	new_data = {'id': new_id, 'name': new_task, 'type': 'task', 'in_cats':[], 'deleted': False}
	data.append(new_data)
	return new_data

def add_category(data, new_category):
	"""Add a new category. Takes data_ids list."""
	new_id = data[-1]['id'] + 1 if data else 0
	data.append({'id': new_id, 'name': new_category, 'type': 'cat', 'in_cats':[], 'deleted': False})

def add_task_category(data, task_id, cat_id):
	"""Adds a task to an existing category"""
	pass

def del_task(data, task_id):
	"""Take task id and sets deleted flag to True. Takes data_ids list."""
	for d in data:
		print d
		if d['id']==task_id:
			d['deleted']=True

def add_checkin(data, task_id):
	"""Takes data_entries list."""
	current_time = dt.datetime.now().strftime("%H:%M")
	new_id = data[-1]['id'] + 1 if data else 0
	new_entry = {'task_id': task_id, 'check_in': current_time, 'id': new_id, 'check_out': ''}
	data.append(new_entry)
	return new_entry

def add_checkout(data, entry_id):
	"""Takes data_entries list."""
	current_time = dt.datetime.now().strftime("%H:%M")
	# data['entries'][-1]['check_out'] = current_time
	# return current_time.strftime("%H:%M")
	for d in data:
		if d['id']==entry_id:
			d['check_out'] = current_time

def del_entry():
	pass 

def del_cat(data, cat_id):
	"""Takes category id and sets deleted flag to True."""
	pass