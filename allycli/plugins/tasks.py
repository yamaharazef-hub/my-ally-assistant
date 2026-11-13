from colorama import Fore

from packages.memory.memory import Memory
from plugin import plugin


@plugin("tasks")
class TaskManager():
    """
    Ally plugin For Managing User Tasks

    """

    def __call__(self, ally, s):
        self.load_tasks()
        ally.say("Welcome To Your Tasks Manager\n")
        while True:
            option = self.get_option(ally)
            if option is None:
                return
            self.procces_chosen_option(option, ally)

    def list_all(self, ally):
        ally.say("")
        task_count = len(self.tasks)
        if task_count == 0:
            ally.say("Your Task List Is Empty, Good Job")
            return
        ally.say("You Have {} {}".format(task_count, "Task" if task_count == 1 else "Tasks"))
        for i in range(task_count):
            try:
                priority = self.tasks[i]["priority"]
                ally.say("{}. {} PR: {}".format(
                    i + 1, self.tasks[i]["name"], priority), self.get_color_with_priority(priority))
            except BaseException:
                ally.say("{}. {}".format(i + 1, self.tasks[i]["name"]))

    def get_color_with_priority(self, priority):
        if priority == "High":
            return Fore.RED
        elif priority == "Medium":
            return Fore.YELLOW
        else:
            return Fore.GREEN

    def add_task(self, ally):
        new_task = ally.input("Enter New Task: ", Fore.GREEN)
        self.tasks.append({"name": new_task})
        self.update_tasks(self.tasks)
        ally.say("Task Was Successfully Added")
        self.list_all(ally)

    def choose_task(self, exit_text, input_text, ally):
        tasks_count = len(self.tasks)
        self.list_all(ally)
        ally.say("{}. {}".format(tasks_count + 1, exit_text))
        return self.get_choice(input_text, tasks_count, tasks_count + 1, ally)

    def update_task(self, ally):
        task_index = self.choose_task("EXIT Editing", "Exit Editing or Choose Which Task To Edit: ", ally)
        if task_index == -1:
            return
        chosen_task_name = self.tasks[task_index - 1]["name"]
        ally.say("Chosen Task: {}".format(chosen_task_name))
        updated_task = ally.input("Enter Updated Task: ", Fore.GREEN)
        new_tasks = map(lambda task: {"name": updated_task} if task["name"] == chosen_task_name else task, self.tasks)
        self.update_tasks(list(new_tasks))
        ally.say("Task Was Successfully Updated")

    def get_priority(self, ally):
        ally.say("")
        ally.say("Choose Priority For Task", Fore.BLUE)
        ally.say("")
        ally.say("1: High")
        ally.say("2: Medium")
        ally.say("3: Low")
        ally.say("4: Exit Priority Mode ")
        ally.say("")
        return self.get_choice("Enter your choice: ", 3, 4, ally)

    def add_priority_to_task(self, ally):
        options = {1: "High", 2: "Medium", 3: "Low"}
        task_index = self.choose_task("EXIT Add Priority Mode",
                                      "Exit Priority Mode or Choose Taks To Add Priority: ", ally)
        if task_index == -1:
            return
        priority = self.get_priority(ally)
        if priority == -1:
            return
        task_name = self.tasks[task_index - 1]["name"]
        new_tasks = map(lambda t: {"name": task_name,
                                   "priority": options[priority]} if t["name"] == task_name else t, self.tasks)
        self.update_tasks(list(new_tasks))

    def delete_task(self, ally):
        task_index = self.choose_task("EXIT Delete Mode", "Exit Delte Mode or Choose Taks To Delete: ", ally)
        if task_index == -1:
            return
        chosen_task_name = self.tasks[task_index - 1]["name"]
        new_tasks = filter(lambda x: x["name"] != chosen_task_name, self.tasks)
        self.update_tasks(list(new_tasks))
        ally.say("Task Was Successfully Deleted")

    def get_sorting_startegy(self, ally):
        ally.say("")
        ally.say("Choose Sorting Strategy", Fore.BLUE)
        ally.say("")
        ally.say("1: By Name")
        ally.say("2: By Priority")
        ally.say("3: Exit Sorting Mode ")
        ally.say("")
        return self.get_choice("Enter your choice: ", 2, 3, ally)

    def display_sorted(self, ally):
        options = {1: "name", 2: "pr"}
        tasks_count = len(self.tasks)
        if tasks_count == 0 | tasks_count == 1:
            ally.say("There is Not Enough Tasks To sort")
            return
        strategy = self.get_sorting_startegy(ally)
        if strategy == -1:
            return

        def sort_by_priority(task):
            try:
                priority = task["priority"]
                if priority == "High":
                    return 3
                elif priority == "Medium":
                    return 2
                else:
                    return 1
            except BaseException:
                return 0

        def sort_by_name(task):
            return task["name"]

        sorted_tasks = self.tasks.copy()
        if options[strategy] == "name":
            sorted_tasks.sort(key=sort_by_name)
        else:
            sorted_tasks.sort(key=sort_by_priority, reverse=True)
        ally.say("")
        for i in range(len(sorted_tasks)):
            try:
                priority = sorted_tasks[i]["priority"]
                color = self.get_color_with_priority(priority)
                ally.say("{}. {} PR: {}".format(i + 1, sorted_tasks[i]["name"], priority), color)
            except BaseException:
                ally.say("{}. {}".format(i + 1, sorted_tasks[i]["name"]))

    def procces_chosen_option(self, option, ally):
        if option == "ann_new":
            self.add_task(ally)
        elif option == "edit_cur":
            self.update_task(ally)
        elif option == "list_all":
            self.list_all(ally)
        elif option == "add_priority":
            self.add_priority_to_task(ally)
        elif option == "delete_task":
            self.delete_task(ally)
        elif option == "sort":
            self.display_sorted(ally)
        else:
            return

    def get_option(self, ally):
        options = {1: "list_all", 2: "ann_new", 3: "edit_cur", 4: "delete_task", 5: "add_priority", 6: "sort"}
        ally.say("")
        ally.say("How Can I Help You?", Fore.BLUE)
        ally.say("")
        ally.say("1: List All My Tasks")
        ally.say("2: Add New Task")
        ally.say("3: Edit Existing Task")
        ally.say("4: Delete  Task")
        ally.say("5: Add Priority To Task")
        ally.say("6: Sort")
        ally.say("7: Exit ")
        ally.say("")
        choice = self.get_choice("Enter your choice: ", 6, 7, ally)
        if choice == -1:
            return
        else:
            return options[choice]

    def get_choice(self, input_text, max_valid_value, terminator, ally):
        while True:
            try:
                inserted_value = int(ally.input(input_text, Fore.GREEN))
                if inserted_value == terminator:
                    return -1
                elif inserted_value <= max_valid_value:
                    return inserted_value
                else:
                    ally.say(
                        "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
            except ValueError:
                ally.say(
                    "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
            ally.say("")

    def load_tasks(self):
        m = Memory("tasks.json")
        if m.get_data("tasks_list") is None:
            self.tasks = []
        else:
            self.tasks = m.get_data("tasks_list")

    def update_tasks(self, new_tasks):
        m = Memory("tasks.json")
        if m.get_data("tasks_list") is None:
            m.add_data("tasks_list", new_tasks)
        else:
            m.update_data("tasks_list", new_tasks)
        m.save()
        self.tasks = new_tasks
