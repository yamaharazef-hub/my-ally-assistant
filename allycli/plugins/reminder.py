import json
import time
import datetime

from pick import pick
from colorama import Fore
from pytimeparse.timeparse import timeparse

from plugin import plugin, alias
from utilities.textParser import parse_date


"""
Module content:
* RemindTodoBase: Shared functionality between Remind and Todo

* TodoBase:  Based on RemindTodoBase; implements functionality required for
              RemindTodoBase to work
* RemindBase: Based on RemindTodoBase; implements functionality required for
              RemindTodoBase to work PLUS other functionality

* RemindTodoInteract_Todo:   Used by TodoBase to access Remind
* RemindTodoInteract_Remind: Used by RemindBase to access Todo (necessary for
                             todo reminders)

* TagBase: Used by TodoBase to apply searchable tags to entries

* Plugins (Todo, Todo_Add, Todo_Incomplete, Todo_Progress, Todo_Remove,
          Remind, Remind_At, Remind_In, Remind_Remove) - oneliner based on
          TodoBase and RemindBase to "export" functionality as Plugins
"""


class TagBase:
    save_key = "reminder_tags"
    next_id_key = "reminder_tags_next_id"

    def load_tags(self, ally):
        tags = ally.get_data(self.save_key)
        if tags is None:
            tags = []
            ally.add_data(self.save_key, [])

        return tags

    def save_tags(self, ally, tags):
        ally.update_data(self.save_key, tags)

    def add_tag(self, ally, name):
        data = self.load_tags(ally)
        new_tag = {
            "id": self.get_next_id(ally),
            "name": name
        }
        data.append(new_tag)
        self.save_tags(ally, data)

    def get_tag_by_id(self, ally, id):
        tags = self.load_tags(ally)
        final_tag = None
        for tag in tags:
            if tag["id"] == id:
                final_tag = tag

        return final_tag

    def get_next_id(self, ally):
        next_id = ally.get_data(self.next_id_key)
        if next_id is None:
            next_id = 0
            ally.add_data(self.next_id_key, next_id)

        ally.update_data(self.next_id_key, next_id + 1)
        return next_id

    def clean_up_entry(self, ally, entry):
        id = entry["id"]
        todos = TodoBase().get_data(ally)
        for todo in todos:
            new_tags = []
            for tag_id in todo["tags"]:
                if tag_id != id:
                    new_tags.append(tag_id)
            todo["tags"] = new_tags
        TodoBase().save_data(ally, todos)

    def format(self, ally, tag):
        return tag["name"]

    def do_print(self, ally):
        tags = self.load_tags(ally)
        for tag in tags:
            ally.say(self.format(ally, tag))

    def select_one_tag(self, ally):
        data = self.load_tags(ally)
        ask_str = []
        for entry in data:
            ask_str.append(self.format(ally, entry))

        if len(ask_str) == 0:
            return None

        title = 'Please choose from tag list (j and k to move up and down, enter to select):'
        _, index = pick(ask_str, title)

        return data[index]

    def remove(self, ally, s):
        data = self.load_tags(ally)
        if len(data) == 0:
            ally.say("Nothing to remove!")
            return

        if s.startswith("everything") or s.startswith("all"):
            for entry in data:
                self.clean_up_entry(ally, entry)

            data = []
            self.save_data(ally, data)

            ally.say("ok")
            return

        # open selection menu
        ask_str = []
        for entry in data:
            ask_str.append(self.format(ally, entry))

        title = 'Please choose tag to remove (select with space, j and k to move up and down)'
        selected = pick(ask_str, title, multi_select=True)
        selected = [entry[1] for entry in selected]

        new_data = []
        for index, entry in enumerate(data):
            entry = data[index]
            if index not in selected:
                new_data.append(entry)
            else:
                self.clean_up_entry(ally, entry)

        self.save_tags(ally, new_data)


class RemindTodoBase:
    def get_data(self, ally):
        remind_todo_json = ally.get_data(self.get_key())
        if remind_todo_json is None:
            remind_todo_json = "[]"
            ally.add_data(self.get_key(), remind_todo_json)

        try:
            remind_todo_list = json.loads(remind_todo_json)
        except json.decoder.JSONDecodeError:
            ally.say(
                "Could not read Remind / Todo List. Sorry, \
                        that should not have happend...", Fore.RED)
            remind_todo_json = "[]"
            ally.update_data(self.get_key(), remind_todo_json)
            remind_todo_list = json.loads(remind_todo_json)

        remind_todo_list = self.sort(remind_todo_list)
        return remind_todo_list

    def save_data(self, ally, remind_todo_list):
        ally.update_data(self.get_key(), json.dumps(remind_todo_list))

    def get_next_id(self, ally):
        next_id = ally.get_data(self.get_key_next_id())
        if next_id is None:
            next_id = 0
            ally.add_data(self.get_key_next_id(), next_id)

        ally.update_data(self.get_key_next_id(), next_id + 1)
        return next_id

    def remove(self, ally, s):
        data = self.get_data(ally)
        if len(data) == 0:
            ally.say("Nothing to remove!")
            return

        if s.startswith("everything") or s.startswith("all"):
            for entry in data:
                self.clean_up_entry(ally, entry)

            data = []
            self.save_data(ally, data)

            ally.say("ok")
            return

        # open selection menu
        ask_str = []
        for entry in data:
            ask_str.append(self.format(ally, entry))

        title = 'Please choose task to remove (select with space, j and k to move up and down)'
        selected = pick(ask_str, title, multi_select=True)
        selected = [entry[1] for entry in selected]

        new_data = []
        for index, entry in enumerate(data):
            entry = data[index]
            if index not in selected:
                new_data.append(entry)
            else:
                self.clean_up_entry(ally, entry)

        self.save_data(ally, new_data)

    def modify(self, ally, modified_entry):
        modified_id = modified_entry['id']
        data = self.get_data(ally)
        data = [entry for entry in data if entry['id'] != modified_id]
        data.append(modified_entry)
        self.save_data(ally, data)

    def do_print(self, ally, should_print=lambda x: True):
        todo_list = self.get_data(ally)

        if len(todo_list) == 0:
            ally.say("No entry!")
        for entry in todo_list:
            if should_print(entry):
                ally.say(self.format(ally, entry))


class TodoBase(RemindTodoBase):
    def interact(self):
        return RemindTodoInteract_Todo()

    def get_key(self):
        return "todo"

    def get_key_next_id(self):
        return "todo_next_id"

    def add(self, ally, message, progress="", priority=-1, tags=[]):
        data = self.get_data(ally)
        next_id = self.get_next_id(ally)
        new_entry = {
            'message': message,
            'progress': progress,
            'priority': priority,
            'id': next_id,
            'tags': []
        }
        data.append(new_entry)
        self.save_data(ally, data)

    def clean_up_entry(self, ally, entry):
        self.interact().clean_up_entry(ally, entry)

    def format(self, ally, entry, addons=['progress', 'tags']):
        message = entry['message']
        schedule = self.interact().format_interact(ally, entry)
        post = ""
        for addon in addons:
            if addon == 'progress':
                progress = entry['progress']
                if progress != '':
                    post += f' | {progress}% complete'

            if addon == 'tags':
                try:
                    tags = entry['tags']
                except KeyError:
                    tags = []

                if len(tags) > 0:
                    tag_base = TagBase()
                    tag_strs = [tag_base.format(ally, tag_base.get_tag_by_id(ally, tag_id))
                                for tag_id
                                in tags]
                    tag_str = ", ".join(tag_strs)
                    post += f' | Tagged with: {tag_str}'
                else:
                    post += ' | No tags'

        return message + post

    def sort(self, todo_list):
        return sorted(todo_list, key=lambda entry: entry['priority'])

    def select_one_remind(self, ally):
        data = self.get_data(ally)
        ask_str = []
        for entry in data:
            ask_str.append(self.format(ally, entry, addons=[]))

        if len(ask_str) == 0:
            return None

        title = 'Please choose from todo list (j and k to move up and down, enter to select):'
        _, index = pick(ask_str, title)

        return data[index]

    def update_to_tags(self, ally):
        data = self.get_data(ally)
        for entry in data:
            try:
                entry["tags"]
            except KeyError:
                entry["tags"] = []

        self.save_data(ally, data)

    def remove_tag(self, ally, s):
        tb = TagBase()
        tags = tb.load_tags(ally)
        entry = self.select_one_remind(ally)
        ask_str = []
        id_map = []
        for tag in tags:
            if tag['id'] in entry['tags']:
                ask_str.append(tb.format(ally, tag))
                id_map.append(tag['id'])

        if len(ask_str) == 0:
            ally.say("There are no tags to delete!")
            return

        title = 'Please choose from tag list (j and k to move up and down, enter to select):'
        _, index = pick(ask_str, title)

        entry['tags'].pop(entry['tags'].index(id_map[index]))

        self.modify(ally, entry)


class RemindBase(RemindTodoBase):
    def interact(self):
        return RemindTodoInteract_Remind()

    def get_key(self):
        return "remind"

    def get_key_next_id(self):
        return "todo_next_id"

    def require(self):
        pass

    def alias(self):
        pass

    def complete(self):
        pass

    def first_time_init(self, ally):
        remind_still_active = []
        for item in self.get_data(ally):
            timestamp = item['timestamp']
            if timestamp < time.time():
                time_format = self.timestamp_to_string(timestamp)
                ally.say(
                    "Reminder: {} missed ({})".format(
                        item['message'], time_format), Fore.MAGENTA)
                continue

            schedule_id = ally.schedule(timestamp, self.reminder_exec,
                                          item['message'])
            item['schedule_id'] = schedule_id
            remind_still_active += [item]
        self.save_data(ally, remind_still_active)

    def add(
            self,
            ally,
            message,
            timestamp=None,
            schedule_id=None,
            todo_refere_id=None):
        data = self.get_data(ally)
        next_id = self.get_next_id(ally)
        new_entry = {
            'message': message,
            'timestamp': timestamp,
            'schedule_id': schedule_id,
            'todo_refere_id': todo_refere_id,
            'id': next_id
        }
        new_data = data + [new_entry]
        self.save_data(ally, new_data)

    def clean_up_entry(self, ally, entry):
        ally.cancel(entry['schedule_id'])

    def format(self, ally, entry):
        time = self.timestamp_to_string(entry['timestamp'])
        additional = self.interact().format_interact(ally, entry)
        return "{} => {}{}".format(time, entry['message'], additional)

    def sort(self, remind_list):
        return sorted(remind_list, key=lambda entry: entry['timestamp'])

    def reminder_exec(self, ally, schedule_id, message):
        ally.notification(message)

        data = self.get_data(ally)
        data = [entry for entry in data if entry['schedule_id'] != schedule_id]
        self.save_data(ally, data)

    def timestamp_to_string(self, timestamp):
        return datetime.datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

    def parse_date_timestamp(self, date):
        date = parse_date(date)
        if date[0] == 0:
            return None
        timestamp = time.mktime(date[1].timetuple())
        return timestamp - time.time()

    def remind_add(self, ally, s, time_in_parser, example):
        s = s.split(" to ")
        if len(s) != 2:
            ally.say("Sorry, please say something like:", Fore.MAGENTA)
            ally.say(" > {}".format(example), Fore.MAGENTA)
            return

        time_in = time_in_parser(s[0])
        while time_in is None:
            ally.say("Sorry, when should I remind you?", Fore.MAGENTA)
            time_in = time_in_parser(ally.input("Time: "))
        timestamp = time.time() + time_in

        message = s[1]
        notification_message = message

        todo_refere_id = None
        if message == 'todo':
            message = ''
            todo_refere_entry = self.interact().select_one_remind(ally)
            if todo_refere_entry is None:
                ally.say("Nothing selected", Fore.MAGENTA)
                return
            notification_message = todo_refere_entry['message']
            notification_message = "TODO: {}".format(notification_message)
            todo_refere_id = todo_refere_entry['id']

        # schedule
        schedule_id = ally.schedule(time_in, self.reminder_exec,
                                      notification_message)
        self.add(ally, message, timestamp=timestamp, schedule_id=schedule_id,
                 todo_refere_id=todo_refere_id)


class RemindTodoInteract_Todo:
    def __init__(self):
        self.remind = RemindBase()

    def clean_up_entry(self, ally, entry):
        todo_id = entry['id']
        remind_list = self.remind.get_data(ally)
        remind_list_new = []
        modify = False
        for entry in remind_list:
            refere = entry['todo_refere_id']
            if refere is not None and refere == todo_id:
                self.remind.clean_up_entry(ally, entry)
                modify = True
            else:
                remind_list_new.append(entry)

        if modify:
            self.remind.save_data(ally, remind_list_new)

    def format_interact(self, ally, entry):
        todo_id = entry['id']
        remind_list = self.remind.get_data(ally)
        remind_list = [remind for remind in remind_list
                       if remind['todo_refere_id'] == todo_id]
        if len(remind_list) != 0:
            remind_list = [self.remind.timestamp_to_string(remind['timestamp'])
                           for remind in remind_list]
            return " -- remind -- ({})".format(', '.join(remind_list))
        return ''


class RemindTodoInteract_Remind:
    def __init__(self):
        self.todo = TodoBase()

    def clean_up_entry(self, ally, entry):
        pass

    def format_interact(self, ally, entry):
        todo_refere_id = entry['todo_refere_id']
        if todo_refere_id is not None:
            todo_list = self.todo.get_data(ally)
            todo = [todo for todo in todo_list if todo['id'] == todo_refere_id]
            if len(todo) != 1:
                return "ERROR"
            else:
                todo = todo[0]
            return "ToDo ->-> {}".format(todo['message'])
        else:
            return ""

    def select_one_remind(self, ally):
        return self.todo.select_one_remind(ally)


# ##################### PLUGIN DEFINITION ##########################
@plugin('todo')
class Todo(TodoBase):
    """
    List todo list
    Usage:
        - todo add make lunch
    """

    def init(self, ally):
        self.update_to_tags(ally)

    def __call__(self, ally, s):
        self.do_print(ally)


@plugin('todo incomplete')
class Todo_Incomplete(TodoBase):
    """
    Lists incomplete todo items.
    """
    def __call__(self, ally, s):
        self.do_print(ally, lambda entry: entry['progress'] < 100)


@plugin('todo add')
class Todo_Add(TodoBase):
    """Add new todo entry"""

    def __call__(self, ally, s):
        self.add(ally, s)


@plugin('todo remove')
class Todo_Remove(TodoBase):
    """
    Remove todo item
    -- Example:
        - todo remove
        - todo remove everything
    """

    def __call__(self, ally, s):
        self.remove(ally, s)


@plugin('todo progress')
class Todo_Progress(TodoBase):
    """
    Set progress info
    """

    def __call__(self, ally, s):
        entry = self.select_one_remind(ally)
        prompt = "Set a progress level between 0 and 100, as a percentage: "
        inp = ally.input(prompt).replace("%", "")

        if inp.isnumeric() and 0 <= int(inp) <= 100:
            entry['progress'] = int(inp)
        else:
            ally.say(
                "The progress level must be an integer between 0 and 100.",
                color=Fore.MAGENTA
            )

        self.modify(ally, entry)


@plugin('todo tag')
class Todo_Tag(TodoBase):
    """
    Add a tag to an item which lets you filter later.
    """
    def __call__(self, ally, s):
        entry = self.select_one_remind(ally)
        tags = TagBase()
        selected_tag = tags.select_one_tag(ally)
        if selected_tag is None:
            ally.say("No tags available to select.")

        try:
            entry["tags"].append(selected_tag["id"])
        except KeyError:
            entry["tags"] = [selected_tag["id"]]

        self.modify(ally, entry)


@plugin('todo del tag')
class Todo_Del_Tag(TodoBase):
    """
    Remove a tag from a todo item.
    """
    def __call__(self, ally, s):
        self.remove_tag(ally, s)


@plugin('todo filter')
class Todo_Filter(TodoBase):
    """
    Filter items on your todo list by tag.
    """
    def __call__(self, ally, s):
        tags = TagBase()
        selected_tag = tags.select_one_tag(ally)
        self.do_print(ally, should_print=lambda entry: selected_tag["id"] in entry["tags"])


@plugin('tags')
class Tags(TagBase):
    """
    List currently created tags.
    """
    def __call__(self, ally, s):
        self.do_print(ally)


@alias('tags create', 'tags add')
@plugin('tags new')
class Tags_New(TagBase):
    """
    Create a new tag.
    """
    def __call__(self, ally, s):
        if not s.isalnum():
            self.add_tag(ally, s)


@plugin('tags remove')
class Tags_Remove(TagBase):
    """
    Remove a pre-existing tag.
    """
    def __call__(self, ally, s):
        self.remove(ally, s)


@plugin('remind')
class Remind(RemindBase):
    """List all scheduled reminders
    Note: Use
    - remind in 5 minutes to todo
    - remind at 12:30 to todo
    To select todo-entry and receive notification.
    """

    def init(self, ally):
        self.first_time_init(ally)

    def __call__(self, ally, s):
        ally.say("## {} ##\n".format(self.timestamp_to_string(time.time())))
        self.do_print(ally)


@plugin('remind at')
class Remind_At(RemindBase):
    """
    Add reminder
    -- Example:
        Remind at 12:30 to buy tomatoes
        Remind at 12:30 to todo
    """

    def __call__(self, ally, s):
        self.remind_add(ally, s, self.parse_date_timestamp,
                        'remind at 12:30 to XXX')


@plugin('remind in')
class Remind_In(RemindBase):
    """
    Add reminder
    -- Example:
        remind in 30 minutes 10 seconds to buy tomatoes
        remind in 30 minutes 10 seconds to todo
    """

    def __call__(self, ally, s):
        self.remind_add(ally, s, timeparse, 'remind in 30m 10s to XXX')


@plugin('remind remove')
class Remind_Remove(RemindBase):
    """
    -- Example:
        remove
        remove everything
    """

    def __call__(self, ally, s):
        self.remove(ally, s)
