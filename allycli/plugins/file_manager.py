import os
import shutil

from plugin import plugin


@plugin("file manage")
class file_manage:
    """"
    Can manipulate files and folders by deleting, moving, or renaming.
    """

    def __call__(self, ally, s):
        self.get_file_directory(ally)
        self.get_cmd(ally)

        if self.cmd == "delete":
            self.delete(ally, self.file)
        elif self.cmd == "move":
            self.move(ally, self.file)
        elif self.cmd == "rename":
            self.rename(ally, self.file)

        # determine if directory entered is a file or folder
        if os.path.isfile(self.file):
            self.folder = False
        else:
            self.folder = True

    def get_file_directory(self, ally):
        self.file = ally.input("Enter the directory of the file you would like to edit: ")

    def get_cmd(self, ally):
        # function to find command to be performed to file

        self.possibleCmds = ["delete", "move", "rename"]

        cmdValid = False
        while not cmdValid:
            # iterate through possible commands and say each
            ally.say("Commands Avaliable")

            i = 1
            for cmd in self.possibleCmds:
                ally.say(str(i) + ". " + cmd)
                i = i + 1

            self.cmd = ally.input("Enter command to be performed: ")

            # check if command is valid. If not, end cycle
            if self.cmd not in self.possibleCmds:
                ally.say("Invalid command")
            else:
                cmdValid = True

    def _confirm_deletion(self, ally):
        while True:
            confirmation = ally.input("Are you sure you want to delete this file? This cannot be undone. (y/n)").lower()
            if confirmation == "y":
                return True
            elif confirmation == "n":
                return False
            ally.say("Invalid input")

    def delete(self, ally, file):
        # function to delete files
        if self.folder is False and os.path.exists(file):
            if self._confirm_deletion(ally):
                try:
                    if not self.folder:
                        os.remove(file)
                    else:
                        os.rmdir(file)
                except:
                    ally.say("Invalid file path")
        else:
            ally.say("file does not exist")

    def move(self, ally, file):
        # function to move files

        path_invalid = True
        while path_invalid:
            # get destination
            dest = ally.input("Where would you like to move this file to? :")

            try:
                # move from old location
                shutil.move(file, dest)
                path_invalid = False
            except:
                ally.say("Invalid path")

    def rename(self, ally, file):
        # function to rename files

        path_invalid = True
        while path_invalid:
            # get new name
            new_name = ally.input("What would you like to rename this file to? :")

            # get root directory
            root = os.path.split(file)[0]

            new_dir = os.path.join(root, new_name)

            try:
                os.rename(file, new_dir)
                path_invalid = False
            except:
                ally.say("Invalid Path")
