
from plugin import plugin,require
from colorama import Fore
import requests
import os
import re


@require(network=True)
@plugin("qr")

class QRGenerator:
    """
    Provides you with a png image of a QR for a specified URL

    Enter 'qr' or 'QR' to use:
    

    Attribution:
        QR generated from https://goqr.me/api/
    """
    
    def __init__(self):
        self.url = "http://api.qrserver.com/v1/create-qr-code/"
    

    def __call__(self,ally,s):
        if s == 'help':
            self._print_help(ally)
            return

        ally.say("\ntype 'qr  help' for additional information")
        ally.say("")

        prompt_url = ("\nType the URL that you want to create a QR code \n" 
                      "or 'end' if you wish to exit: ")
        # get url from user prompt
        url = self._get_url(prompt_url,ally)
        if url == "end":
            return
        ally.say("")

        prompt_path = ("\nType the filepath where you want the QR to be stored \n"
                       "or 'end' if you wish to exit: ")
        # get path from user prompt
        self.path = self._get_path(prompt_path,ally)
        if self.path == "end":
            return
        ally.say("")

        prompt_name = ("\nEnter the name of the png file that will be created: ")
        # get filename from user prompt
        name = ally.input(prompt_name,Fore.CYAN)
        # replace whitespaces with underscores
        name = name.strip().replace(' ', '_')
        self.filename = re.sub(r'(?u)[^-\w.]', '', name)
        # generate query and add the needed parameters 
        query = self.url + "?data=" + url + "&size=250x250"
        # generate QR code from the query
        self._generate_qr(ally,query)

        return
    


    def _get_url(self, prompt, ally):
        """
        checks if the URL the user gave is in valid form(can be reached).
        The user can type 'end' to exit in case his URL is continuously rejected.
        The method covers the basic exceptions created by invalid URLs.
        """

        while True:
            try:
                response = ally.input(prompt,Fore.CYAN)
                # the user wants to exit
                if response == "end":
                    break
                # tries to get website from URL 
                website = requests.get(response)
                break
            # list of possible exceptions from URLs with invalid form
            except requests.exceptions.MissingSchema:
                ally.say("\nSorry, your input URL is not valid.",Fore.RED)
                ally.say("Try something in this form 'https://github.com/.../...'")
            # handles the exception where the user misses part of the 'http' part of the URL
            except requests.exceptions.InvalidSchema:
                ally.say("\nSorry, your input URL is not valid.",Fore.RED)
                ally.say("Try something in this form 'https://github.com/.../...'")
            except requests.exceptions.ConnectionError:
                ally.say("\nSorry, your input URL is not valid.",Fore.RED)
                ally.say("Try something in this form 'https://github.com/.../...'")
            except requests.exceptions.InvalidURL:
                ally.say("\nSorry, your input URL is not valid.",Fore.RED)
                ally.say("Try something in this form 'https://github.com/.../...'")
                
        return response
    

    def _get_path(self, prompt, ally):
        """
        checks if the path the user gave is valid(directory exists on the computer).
        The user can type 'end' to exit in case his path is continuously rejected.
        """

        while True:
            path = ally.input(prompt,Fore.CYAN)
            # the user wants to exit
            if path == "end":
                response = path
                break
            isFile = os.path.isdir(path)
            # directory exists
            if isFile:
                response = path
                break
            ally.say("\nSorry, the path that you specified couldn't be found",Fore.RED)
            ally.say("Try something in this form 'C:\..\..' if you are using Windows for example.")
            
        return response
    
    def _generate_qr(self, ally, query):
        try:
            # send request
            ally.spinner_start('Creating QR ')
            response = requests.get(query)
            # where the png file will be stored
            location = os.path.join(self.path,self.filename + '.png')
            file = open(location, "wb")
            file.write(response.content)
            ally.spinner_stop()
            file.close()
        except requests.exceptions.RequestException as e:
            ally.spinner_stop(
            message="\nUrl request failed!", color=Fore.RED)
        except IOError as e:
            ally.spinner_stop(
            message="\nFile operation failed!", color=Fore.RED)
        finally:
            return

        

    # manual for plugin
    def _print_help(self, ally):
        ally.say("\nWelcome to QR Generator!", Fore.CYAN)
        ally.say("You can use current plugin as follows:", Fore.CYAN)
        ally.say("    'qr' or 'QR' ", Fore.CYAN)
        ally.say(    
            "Result: The user receives a png image containing a QR.", Fore.CYAN)
        ally.say(    
            "        The QR code leads to the URL the user specified, and it is stored on a directory of his choice!", Fore.CYAN)
        ally.say("\nExample: ", Fore.CYAN)
        ally.say(
            "         'qr' - initial call ", Fore.CYAN)
        ally.say(
            "         'https://github.com/sukeesh/Ally' - valid URL or type 'end' to exit ", Fore.CYAN)
        ally.say(
            "         'C:\\Users\\Public\\Downloads' -  valid file location or type 'end' to exit ", Fore.CYAN)
        ally.say(
            "         'ally_qr' - name of the png file ", Fore.CYAN)
        ally.say(
            "The steps above create a QR code on the specified directory that leads to Jarvi's central page on GitHub!", Fore.CYAN)

    