# Just USe a button for the taskselector dropdown
# need to make sure empty task aren't added in task selector screen
# t_list.sort(key=lambda r: datetime.datetime.strptime(r['start'], "%Y-%m-%d %H:%M:%S.%f"))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.listview import ListItemButton
from kivy.factory import Factory
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button

import datetime as dt

class TimeTrackRoot(BoxLayout):

	time_record_screen = ObjectProperty()
	task_selector = ObjectProperty()
	task_add_input = ObjectProperty()
	manual_add = ObjectProperty()
	
	def __init__(self, **kwargs):
		super(TimeTrackRoot, self).__init__(**kwargs)
		self.task_list = []
		self.running_task = None
		self.entry_dict = {}
		self.date_list_widgets = {} # keeps references to all date_list objects so they can be easily changed later
		#dt.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")

	def open_task_selector(self):
		self.task_selector = Factory.TaskSelector()
		self.task_selector.task_list.adapter.data = self.task_list
		self.task_selector.open()

	def open_task_add_input(self):
		if 'task_add_input' not in self.task_selector.ids:
			self.task_add_input = Factory.TaskAddInput()
			self.task_selector.content.add_widget(self.task_add_input)

	def open_manual_add(self):
		self.manual_add = ManualAdd()
		self.manual_add.open()

	def add_task(self, task_name):
		new_task = {'id': self.task_list[-1]['id'] + 1 if self.task_list else 0, 'name': task_name}
		self.task_list.append(new_task)
		print self.task_list
		if self.task_selector: #I should move this...
			self.task_selector.task_list.adapter.data = self.task_list
			self.task_selector.task_list._trigger_reset_populate()
			self.task_selector.content.remove_widget(self.task_add_input)
		return new_task

	def start_timer(self, task_id , task_name):
		self.task_selector.dismiss()
		self.time_record_screen.task_buttons.clear_widgets()
		task_label = Label(text='[b]'+task_name+'[/b]', pos_hint={'top': 1}, size_hint_y=None, height="40dp", markup=True)
		self.time_record_screen.task_buttons.add_widget(task_label)
		task_timer = TaskTimer()
		self.time_record_screen.task_buttons.add_widget(task_timer)
		self.time_record_screen.task_buttons.add_widget(Factory.SwitchButton())
		self.time_record_screen.task_buttons.add_widget(Factory.EndButton())
		Clock.schedule_interval(task_timer.update, 1)
		self.running_task = {'id': task_id, 'name': task_name, 'start_time': str(task_timer.start_time)} #conversion necessary for storing in JSon

	def end_timer(self):
		start_time = self.datify(self.running_task['start_time'])
		start_day = start_time.strftime("%A, %d %B %Y")
		if start_day in self.entry_dict:
			new_entry = {'id': self.entry_dict[start_day][-1]['id'] + 1,
						'task_id': self.running_task['id'],
						'task_name': self.running_task['name'],
						'start_time': self.running_task['start_time'],
						'end_time': str(dt.datetime.now())}
			self.entry_dict[start_day].append(new_entry)
			self.add_entry(new_entry, start_day)
		else:
			new_entry = {'id': 0,
					   'task_id': self.running_task['id'],
					   'task_name': self.running_task['name'],
					   'start_time': self.running_task['start_time'],
					   'end_time': str(dt.datetime.now())}
			self.entry_dict[start_day] = [new_entry]
			self.add_entry(new_entry, start_day, True)
		self.running_task = None
		self.time_record_screen.task_buttons.clear_widgets()
		self.time_record_screen.task_buttons.add_widget(Factory.StartButton())
		# print self.entry_dict

	def switch_timer(self):
		print "Timer switched."

	def add_entry(self, new_entry, start_day, new_day=False): # [TODO] check order of datelists
		duration =  self.datify(new_entry['end_time']) - self.datify(new_entry['start_time'])
		duration = duration.seconds
		entry_name_button = Factory.EntryNameButton()
		entry_name_button.text = new_entry['task_name']
		entry_duration_button = Factory.EntryDurationButton()
		entry_duration_button.text = '{:02}:{:02}'.format(duration // 3600, duration % 3600 // 60)
		entry_start_stop_button = Factory.EntryStartStopButton()
		entry_start_stop_button.text = new_entry['start_time'][11:16] +'-'+new_entry['end_time'][11:16]

		if new_day:
			date_list = Factory.DateList()
			date_list.date = start_day
			date_list.entries_list.add_widget(entry_name_button)
			date_list.entries_list.add_widget(entry_duration_button)
			date_list.entries_list.add_widget(entry_start_stop_button)
			self.date_list_widgets[start_day] = date_list 
			if self.time_record_screen.entries.children:
				self.time_record_screen.entries.add_widget(date_list, len(self.time_record_screen.entries.children))
			else:
				self.time_record_screen.entries.add_widget(date_list)
		else:
			length = len(self.date_list_widgets[start_day].entries_list.children)
			self.date_list_widgets[start_day].entries_list.add_widget(entry_name_button, length) # adds new entries to top
			self.date_list_widgets[start_day].entries_list.add_widget(entry_duration_button, length)
			self.date_list_widgets[start_day].entries_list.add_widget(entry_start_stop_button, length)

	def add_manual_entry(self, start_day, new_entry):
		"""Decides where to add entry from ManualAdd if it is a valid entry."""
		if start_day in self.entry_dict:
			temp_d = self.entry_dict[start_day][:] #copy list of entries for under start_day to sort and check for clashes
			temp_d.append(new_entry)
			temp_d.sort(key=lambda r: self.datify(r['start_time']))
			if self.is_clash(temp_d):
				# some kind of error message, maybe ManualAdd shouldn't dismiss until this point
				# so not all data has to be re-entered by user.
				return
			self.date_list_widgets[start_day].entries_list.clear_widgets()
			for entry in temp_d: # [TODO] add new entry without rebuilding entire datelist
				duration =  self.datify(entry['end_time']) - self.datify(entry['start_time'])
				duration = duration.seconds
				entry_name_button = Factory.EntryNameButton()
				entry_name_button.text = entry['task_name']
				entry_duration_button = Factory.EntryDurationButton()
				entry_duration_button.text = '{:02}:{:02}'.format(duration // 3600, duration % 3600 // 60)
				entry_start_stop_button = Factory.EntryStartStopButton()
				entry_start_stop_button.text = entry['start_time'][11:16] + '-' + entry['end_time'][11:16]
				length = len(self.date_list_widgets[start_day].entries_list.children)
				self.date_list_widgets[start_day].entries_list.add_widget(entry_name_button, length) # adds new entries to top
				self.date_list_widgets[start_day].entries_list.add_widget(entry_duration_button, length)
				self.date_list_widgets[start_day].entries_list.add_widget(entry_start_stop_button, length)

			self.entry_dict[start_day].append(new_entry)
		
		else:
			duration =  self.datify(new_entry['end_time']) - self.datify(new_entry['start_time'])
			duration = duration.seconds
			entry_name_button = Factory.EntryNameButton()
			entry_name_button.text = new_entry['task_name']
			entry_duration_button = Factory.EntryDurationButton()
			entry_duration_button.text = '{:02}:{:02}'.format(duration // 3600, duration % 3600 // 60)
			entry_start_stop_button = Factory.EntryStartStopButton()
			entry_start_stop_button.text = new_entry['start_time'][11:16] +'-'+new_entry['end_time'][11:16]
			date_list = Factory.DateList()
			date_list.date = start_day
			date_list.entries_list.add_widget(entry_name_button)
			date_list.entries_list.add_widget(entry_duration_button)
			date_list.entries_list.add_widget(entry_start_stop_button)
			self.date_list_widgets[start_day] = date_list

			if self.time_record_screen.entries.children:
				self.date_list_widgets.sort(key=lambda r: dt.datetime.strptime(r.date, "%A, %d %B %Y"), reverse=True)
				insert_at = self.date_list_widgets.index(date_list)
				self.time_record_screen.entries.add_widget(date_list, insert_at)
			else:
				self.time_record_screen.entries.add_widget(date_list)



	def datify(self, date_text):
		"""Convert date_text string into datetime object"""
		return dt.datetime.strptime(date_text, "%Y-%m-%d %H:%M:%S.%f")

	def is_clash(self, d_list):
		"""Checks if a manually added entry clashes with an already existing one.
		Used in `self.add_manual_entry`."""
		prev_item = None
		for index, entry in enumerate(d_list):
		    if not prev_item:
		        prev_item = entry
		        continue
		    if self.datify(entry['start_time']) < self.datify(prev_item['end_time']):
		        return True
		    prev_item = entry
		    return False

	
class ManualAdd(Popup):

	task_drop = ObjectProperty()

	def error_message(self, message):
		error_pop = Factory.ErrorMessage()
		error_pop.message = message
		error_pop.open()
		Clock.schedule_once(lambda dt: error_pop.dismiss(), 3)

	def process_manual_entry(self):
		if not self.ids.day_input.text:
			self.error_message("You must enter value for day.")
		elif not self.ids.month_input.text:
			self.error_message("You must enter value for month.")
		elif not self.ids.year_input.text:
			self.error_message("You must enter value for year.")
		elif len(self.ids.year_input.text) != 4:
			self.error_message("Input for year must be 4 digits long.")
		elif self.wrong_day(self.ids.day_input.text, self.ids.month_input.text, 
			self.ids.year_input.text):
			self.error_message("Day, Month and Year do not match up.")
		elif (not self.ids.check_in_minute.text) or (not self.ids.check_in_hour.text):
			self.error_message("Enter a value for check in time.")
		elif (not self.ids.check_out_minute.text) or (not self.ids.check_out_hour.text):
			self.error_message("Enter a value for check out time.")
		else:
			year_text = "{}-{:0>2}-{:0>2}".format(self.ids.year_input.text,
				self.ids.month_input.text, self.ids.day_input.text)
			format_start = "{} {:0>2}:{:0>2}:00.0".format(year_text, self.ids.check_in_hour.text, self.ids.check_in_minute.text)
			format_end = "{} {:0>2}:{:0>2}:00.0".format(year_text, self.ids.check_out_hour.text, self.ids.check_out_minute.text)
			start_day = dt.datetime.strptime(year_text, "%Y-%m-%d").strftime("%A, %d %B %Y")
			# print start_day + '\n' + format_start + '\n' + format_end
			root = TimeTrackApp.get_running_app().root
			new = False if start_day in root.entry_dict else True
			new_entry = {'id': 0 if new else root.entry_dict[start_day][-1]['id'] + 1,
						'task_id': self.task_id,
						'task_name': self.task_name,
						'start_time': format_start,
						'end_time': format_end}
			root.add_manual_entry(start_day, new_entry)
			self.dismiss()

	def open_task_drop(self):
		self.task_drop = TaskDrop()
		self.task_drop.open(self.ids.task_selector)

	def wrong_day(self, day, month, year):
		long = [1, 3, 5, 7, 8, 10, 12]
		if (int(year)%4) != 0:
			leap_year = False
		elif (int(year)%100) != 0:
			leap_year = True
		elif (int(year)%400) != 0:
			leap_year = False
		else:
			leap_year = True

		if (int(month) not in long) and (int(day) > 30):
			return True
		if (int(month)==2) and (int(day) > 29):
			return True
		elif (int(month)==2) and (not leap_year) and  (int(day) > 28):
			return True
		else:
			return False

class TimeRecordScreen(BoxLayout):
	pass

class TaskDrop(DropDown):
	def __init__(self, **kwargs):
		super(TaskDrop, self).__init__(**kwargs)
		self.root = TimeTrackApp.get_running_app().root
		task_list = self.root.task_list
		for task in task_list:
			butt = Factory.ManualTaskButton()
			butt.text=task['name']
			butt.task_id = task['id']
			self.add_widget(butt)
		# self.load_tasks()
		# self.task_add = TextInput(size_hint_y=None, height="40dp", hint_text="Add new task.", multiline=False)
		# self.task_add.bind(on_text_validate=self.root.add_task(self.task_add.text))
		# self.add_widget(self.task_add)
	
	# def load_tasks(self):
	# 	self.clear_widgets(children=self.children[1:])
	# 	task_list = self.root.task_list
	# 	for task in task_list:
	# 		butt = Button(text=task['name'], size_hint_y=None, height="40dp")
	# 		self.add_widget(butt)

	def add_task(self, task_name):
		if task_name:
			new_task = self.root.add_task(task_name)
			self.ids.text_input.text = ''
			butt = Factory.ManualTaskButton()
			butt.text = new_task['name']
			butt.task_id = new_task['id']
			self.add_widget(butt)

	def on_select(self, value):
		# print "{}, with id {} selected.".format(*value)
		self.root.manual_add.ids.task_selector.text = self.root.manual_add.task_name = value[0]
		self.root.manual_add.task_id = value[1]

class TaskListButton(ListItemButton):
	task_id = NumericProperty()

class TaskTimer(Label):
	def __init__(self, **kwargs):
		super(TaskTimer, self).__init__(**kwargs)
		self.text = "00:00:00"
		self.start_time = dt.datetime.now()

	def update(self, *args):
		elapsed = dt.datetime.now() - self.start_time
		s = elapsed.seconds
		self.text = '{:02}:{:02}:{:02}'.format(s // 3600, s % 3600 // 60, s % 60)

class NumberInput(TextInput):
	
	def __init__(self, **kwargs):
		super(NumberInput, self).__init__(**kwargs)
		self.input_type = 'number'
		self.multiline = False
		self.font_size = "40dp"
		self.write_tab = False
		self.max_length = 2
		self.zero_pad = True
		self.min_val = 0
		self.max_val = 9999
		

	def on_focus(self, instance, value):
		if value and self.text:
			Clock.schedule_once(lambda dt: self.select_all())
		if not value and self.text:
			self.text = self.text.zfill(self.max_length)
	
	def insert_text(self, substring, from_undo=False):
		if not from_undo:
			try:
				int(substring)
				if (int(self.text + substring) > self.max_val):
					return
				elif ((len(self.text) + len(substring)) == self.max_length):
					super(NumberInput, self).insert_text(substring, from_undo)
					nxt = self._get_focus_next('focus_next')
					if nxt:
						self.focused = False
						nxt.focused = True
				else:
					super(NumberInput, self).insert_text(substring, from_undo)
			except ValueError:
				return

class HourInput(NumberInput):
	
	def __init__(self, **kwargs):
		super(HourInput, self).__init__(**kwargs)
		self.max_val = 23

class MinuteInput(NumberInput):	
	
	def __init__(self, **kwargs):
		super(MinuteInput, self).__init__(**kwargs)
		self.max_val = 59

class DayInput(NumberInput):
	
	def __init__(self, **kwargs):
		super(DayInput, self).__init__(**kwargs)
		self.max_val = 31

class MonthInput(NumberInput):
	
	def __init__(self, **kwargs):
		super(MonthInput, self).__init__(**kwargs)
		self.max_val = 12

class YearInput(NumberInput):
	def __init__(self, **kwargs):
		super(YearInput, self).__init__(**kwargs)
		self.max_length = 4
		self.zero_pad = False

class TimeTrackApp(App):
	pass

def task_list_args(index, data_item):
	return {'task_id': data_item['id'],
			'text': data_item['name']}

if __name__=='__main__':
	TimeTrackApp().run()
