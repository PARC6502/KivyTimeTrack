 

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, ListProperty
from kivy.uix.listview import ListItemButton
from kivy.factory import Factory
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
import datetime as dt
import datamanage

class TimeTrackRoot(BoxLayout):

	"""Root widget of application.

	task_list_screen -- kivy property which points to TaskListScreen. Not always initialised.
	time_record_screen -- kivy property which points to TimeRecordScreen.
	task_manage_screen -- kivy property which points to TaskManageScreen.
	data -- dictionary which contains tasks/ids/etc."""

	task_list_screen = ObjectProperty()
	time_record_screen = ObjectProperty()
	task_manage_screen = ObjectProperty()
	task_creator_screen = ObjectProperty()
	data_ids = ListProperty([])
	data_entries = ListProperty([])
	
	def __init__(self, **kwargs):
		super(TimeTrackRoot, self).__init__(**kwargs)
		
		self.store = JsonStore("time_track_store.json")
		if self.store.exists('data_ids'):
			self.data_ids = self.store.get('data_ids')['data_ids']
		if self.store.exists('data_entries'):
			self.data_entries = self.store.get('data_entries')['data_entries']
			# print store['data']
		# else:
		# 	self.data = {'ids': [], 
		# 	'entries': []}
		# 	#print self.store['data']

		self.task_manage_screen.task_list.adapter.data = datamanage.list_all_tasks(self.data_ids)
		# print self.task_manage_screen.task_list.adapter.data

	def on_data_ids(self, instance=None, value=None):
		# Need to make tasklistscreen Update from here, and change the way tasks are added
		self.task_manage_screen.task_list.adapter.data = datamanage.list_all_tasks(self.data_ids)
		self.task_manage_screen.task_list._trigger_reset_populate()
		self.task_manage_screen.add_to_cat_buttons.adapter.data = datamanage.list_all_tasks(self.data_ids)
		self.task_manage_screen.add_to_cat_buttons._trigger_reset_populate()
		self.task_manage_screen.delete_task_buttons.adapter.data = datamanage.list_all_tasks(self.data_ids)
		self.task_manage_screen.delete_task_buttons._trigger_reset_populate()
		if not instance: #required because it doesn't update if dictionary has been changed w/o data being added
			self.task_manage_screen.task_list.adapter.update_for_new_data()
			self.task_manage_screen.add_to_cat_buttons.adapter.update_for_new_data()
			self.task_manage_screen.delete_task_buttons.adapter.update_for_new_data()
		self.store.put('data_ids', data_ids=self.data_ids)

	def on_data_entries(self, instance=None, value=None):
		# print 'on_data_entries called'
		self.time_record_screen.check_in.adapter.data = self.data_entries
		self.time_record_screen.check_in._trigger_reset_populate()
		self.time_record_screen.check_out.adapter.data = self.data_entries
		self.time_record_screen.check_out.adapter.update_for_new_data()
		self.time_record_screen.check_out._trigger_reset_populate()
		self.time_record_screen.task_list.adapter.data = self.data_entries
		self.time_record_screen.task_list._trigger_reset_populate()
		self.store.put('data_entries', data_entries=self.data_entries)

	def add_task_list_screen(self, switch=False):
		"""Open Task List Screen.

		TaskListScreen is opened from the Time Record Screen, and is used to add entries. 
		The variable 'switch' indicates whether it was opened using 'Start' or 'Switch', 
		which is set as (kivy) property of TaskListScreen 
		"""
		self.task_list_screen = TaskListScreen()
		self.task_list_screen.task_list.adapter.data.extend(datamanage.list_all_tasks(self.data_ids))
		self.task_list_screen.open()
		self.task_list_screen.switch = switch

	def add_check_in(self, task_id):
		"""Add entry with task and check in time (current time) to TimeRecordScreen. 
		Change button from 'Start' to 'Switch' and 'End' if there is a task running.
		Add check out time if a new task is added using 'Switch'."""
		# print task_id

		if self.task_list_screen.switch:
			datamanage.add_checkout(self.data_entries, self.current_entry)
		else:
			self.time_record_screen.task_buttons.clear_widgets()
			self.time_record_screen.task_buttons.add_widget(Factory.SwitchButton())
			self.time_record_screen.task_buttons.add_widget(Factory.EndButton())

		self.task_list_screen.dismiss()
		new_checkin = datamanage.add_checkin(self.data_entries, task_id)
		self.current_entry = new_checkin['id']

	def end_task(self):
		datamanage.add_checkout(self.data_entries, self.current_entry)
		self.on_data_entries()
		# print self.data_entries
		# self.time_record_screen.check_out.adapter.data = self.data['entries'][1:]
		# self.time_record_screen.check_out._trigger_reset_populate()
		self.time_record_screen.task_buttons.clear_widgets()
		self.time_record_screen.task_buttons.add_widget(Factory.StartButton())
		# self.store['data'] = self.data
		# print store['data']

	def open_task_creator(self):
		self.task_creator_screen = TaskCreatorScreen()
		self.task_creator_screen.open()

	def create_new_task(self, task_name):
		new_data = datamanage.add_task(self.data_ids, task_name)
		# self.task_manage_screen.task_list.adapter.data.append(new_data)
		# self.task_manage_screen.task_list._trigger_reset_populate()
		self.task_creator_screen.dismiss()
		#print self.task_manage_screen.task_list.adapter.data
		# print  self.data

	def delete_task(self, task_id):
		datamanage.del_task(self.data_ids, task_id)
		# print self.data_ids
		self.on_data_ids()

	def add_to_cat(self, task_id):
		pass

class TimeRecordScreen(BoxLayout):
	pass

class TaskManageScreen(BoxLayout):
	pass

class TaskListScreen(ModalView):
	pass

class TaskListButton(ListItemButton):
	task_id = NumericProperty()

class TaskManageButton(ListItemButton):
	pass

class TimeRecordButton(ListItemButton):
	check_in = StringProperty()
	check_out = StringProperty()
	entry_id = NumericProperty()
	task_id = NumericProperty()
	task_name = StringProperty()

class CheckinButton(TimeRecordButton):
	pass

class CheckoutButton(TimeRecordButton):
	pass

class TaskNameButton(TimeRecordButton):
	pass

class TaskCreatorScreen(ModalView):
	pass

class AddToCatButton(ListItemButton):
	task_id = NumericProperty()

class DeleteTaskButton(ListItemButton):
	task_id = NumericProperty()

class TimeTrackApp(App):
	pass

def tasks_args_converter(index, data_item):
	return {'text': data_item['name'],
			'task_id': data_item['id']}

def checkin_args_converter(index, data_item):
		return {'text': data_item['check_in'],
				'task_id': data_item['task_id'],
				'entry_id': data_item['id']}

#Clock.schedule_interval(lambda x: dt.datetime.now().strftime("%H:%M"), 60)
def checkout_args_converter(index, data_item):
	if not data_item['check_out']:
		return {'text': '',
				'task_id': data_item['task_id'],
				'entry_id': data_item['id']}
	else:
		return {'text': data_item['check_out'],
				'task_id': data_item['task_id'],
				'entry_id': data_item['id']}

def taskname_args_converter(index, data_item):
	return {'task_id': data_item['task_id'],
			'entry_id': data_item['id'],
			'text': str(datamanage.get_task_name(TimeTrackApp.get_running_app().root.data_ids, data_item['task_id']))}

def add_cat_args_converter(index, data_item):
	return {'task_id': data_item['id'],
			'text': 'Add Category'}

def delete_task_args_converter(index, data_item):
	return {'task_id': data_item['id'],
			'text': 'Delete'}

if __name__=='__main__':
	TimeTrackApp().run()