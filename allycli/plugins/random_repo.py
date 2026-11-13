# All plugins should inherite from this library
from github3 import login,GitHub, exceptions
from colorama import Fore
from random import randint
from plugin import alias, plugin, require
# This is the standard form of a plugin for ally

# Anytime you make a change REMEMBER TO RESTART Ally

# You can run it through ally by the name
# in the @plugin tag.


class RandomProjectPicker:
    def getRandomRepo(self,repo_gen,ally):
        repos=[]
        try:
           for repo in repo_gen:
               repos.append(repo)
           n=len(repos)
           ally.say("Number of repo: "+str(n),Fore.YELLOW)
           chosen_repo=repos[randint(0,n-1)];
           ally.say("The Chosen repo is: "+chosen_repo.name,Fore.YELLOW)
        except(exceptions.NotFoundError):
            ally.say("User Not Found!",Fore.RED)
        self.run(ally)
    def loginWithToken(self,ally):
        auth_token = ally.input("Give Ally your Github Access Token: ",Fore.YELLOW)
        try:
            g=login(token=auth_token)
            g.me()
            repo_gen=g.repositories(type='owner')
            self.getRandomRepo(repo_gen,ally)
        except(exceptions.AuthenticationFailed):
            ally.say("Inavlid Access Token!",color=Fore.RED)
            self.run(ally)

    def noLogin(self,ally):
        username = ally.input("Give Ally your Github username: ",Fore.YELLOW)
        g=GitHub()
        #try:
        repo_gen=g.repositories_by(username)
        self.getRandomRepo(repo_gen,ally)
            
    def run(self,ally):
    
        ally.say("Choose login method:",color=Fore.YELLOW)
        ally.say("1. With Personal Access Token.",color=Fore.YELLOW)
        ally.say("2. No login.",color=Fore.YELLOW)
        ally.say("3. Close.",color=Fore.YELLOW)
        choice=ally.input("Enter your choice: ",color=Fore.GREEN).strip();
        while (choice<"1" or choice>"3"):
            ally.say("Invalid choice!",color=Fore.RED)
            choice=ally.input("Enter your choice: ",color=Fore.GREEN).strip();
        if (choice =="1"):
            RandomProjectPicker().loginWithToken(ally)
        elif (choice == "2"):
            RandomProjectPicker().noLogin(ally)

@alias('random github repo')
@require(network=True)
@plugin('random repo')

def my_plugin(ally, s):
    RandomProjectPicker().run(ally)

