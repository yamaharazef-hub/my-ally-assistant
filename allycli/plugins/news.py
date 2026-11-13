# !!! This uses the https://newsapi.org/ api. TO comply with the TOU
# !!! we must link back to this site whenever we display results.
import json
import requests
import webbrowser
from colorama import Fore
from plugin import plugin, require


@require(network=True)
@plugin('news')
class News:

    def __init__(self):
        self.sources = [
            'bloomberg',
            'financial-times',
            'cnbc',
            'reuters',
            'al-jazeera-english',
            'the-wall-street-journal',
            'the-huffington-post',
            'business-insider',
            'the-new-york-times',
            'abc-news',
            'fox-news',
            'cnn',
            'google-news',
            'wired']
        self.source_dict = {}

        for source in self.sources:
            self.source_dict[str(self.sources.index(source) + 1)] = source

    def __call__(self, ally, s):
        if s == "updatekey":
            key = ally.input(
                "Please enter your NEWS API key (q or Enter go back): ")
            if key.lower() == "q" or key.lower() == "":
                ally.say("Could not update the NEWS API key! ", Fore.RED)
            else:
                self.update_api_key(ally, key)
                ally.say("NEWS API key successfully updated! ", Fore.GREEN)
        elif s == "configure":
            self.configure(ally)
        elif s == "remove":
            self.remove_source(ally)
        elif s == "help":
            ally.say("-------------------------------------")
            ally.say("Command\t\t | Description")
            ally.say("-------------------------------------")
            ally.say("news\t\t : Finds top headlines")
            ally.say(
                "news updatekey\t : Updates the news API key of the user")
            ally.say(
                "news configure\t : Configures the news channel of the user")
            ally.say("news sources\t : List the configured news sources")
            ally.say(
                "news remove\t : Removes a source from the news channel of the user")
            ally.say("news [word]\t : Finds articles related to that word")
        elif s == "sources":
            sources = self.get_news_sources(ally)
            if not sources:
                ally.say(
                    "No sources configured. Use 'news configure' to add sources.",
                    Fore.RED)
            else:
                dic = {}
                for source in sources:
                    dic[str(sources.index(source) + 1)] = source

                for index in sorted([int(x) for x in dic.keys()]):
                    ally.say(str(index) + " : " + dic[str(index)])
        elif self.get_api_key(ally) is None:
            ally.say("Missing API key", Fore.RED)
            ally.say("Visit https://newsapi.org/ to get the key", Fore.RED)
            ally.say(
                "Use \'news updatekey\' command to add a key\n",
                Fore.RED)
        elif s == "" or s == " ":
            self.parse_articles(self.get_headlines(ally), ally)
        else:
            searchlist = s.split(" ")
            if "" in searchlist:
                searchlist.remove("")
            if " " in searchlist:
                searchlist.remove(" ")
            self.parse_articles(self.get_news(ally, searchlist), ally)

    @staticmethod
    def get_api_key(ally):
        """
            will return either the news_api key of the user, already stored in the memory.json
            file or None in case the user does not have his own api
        """
        return ally.get_data("news-settings")

    def update_api_key(self, ally, api_key):
        """
            the user might have a news api key and they might want to add to memory.json or update an old one
        """
        ally.update_data("news-settings", api_key)
        return self.get_api_key(ally)

    def get_news_sources(self, ally):
        """
            returns a list of all the new sources added to the news channel of the user
        """
        sources = ally.get_data("news-sources")
        if sources is None:
            sources = []
        return sources

    def add_source(self, ally, news_source):
        """
            adds a new source (if it does not exist) to the news channel of the user
        """
        sources = self.get_news_sources(ally)
        if news_source not in sources:
            sources.append(news_source)
            ally.update_data("news-sources", sources)
            ally.say(
                news_source
                + " has been successfully been added to your sources!",
                Fore.GREEN)
        else:
            ally.say(
                news_source
                + " was already included in your sources!",
                Fore.GREEN)
        return self.get_news_sources(ally)

    def remove_source(self, ally):
        """
            removes a new source from the news channel of the user
        """
        sources = self.get_news_sources(ally)

        dic = {}
        for source in sources:
            dic[str(sources.index(source) + 1)] = source

        for index in sorted([int(x) for x in dic.keys()]):
            ally.say(str(index) + " : " + dic[str(index)])
        index_list = ally.input(
            "Type the indexes of the sources you would like to remove from your channel separated by "
            "space: ")
        index_list = index_list.split(" ")
        if " " in index_list:
            index_list.remove(" ")
        if "" in index_list:
            index_list.remove("")
        for index in index_list:
            if str(index) in dic:
                source = dic[str(index)]
                sources.remove(source)
                ally.update_data("news-sources", sources)
                ally.say(
                    source
                    + " has been successfully removed from your news channel!",
                    Fore.GREEN)
            else:
                ally.say("Index not found!", Fore.RED)
        return self.get_news_sources(ally)

    def configure(self, ally):
        """
            configures the news channel of the user
        """
        for index in sorted([int(x) for x in self.source_dict.keys()]):
            ally.say(str(index) + ": " + self.source_dict.get(str(index)))
        index_list = ally.input(
            "Type the indexes of the sources you would like to add to your channel separated by "
            "space: ")
        index_list = index_list.split(" ")
        if " " in index_list:
            index_list.remove(" ")
        if "" in index_list:
            index_list.remove("")
        for index in index_list:
            if index in self.source_dict.keys():
                self.add_source(ally, self.source_dict.get(index, index))
            else:
                ally.say(index + " is not a valid index", Fore.RED)

    def get_headlines(self, ally):
        """
            gets top headlines for a quick lookup of the world news, based on the news channel of the user (if it exists)
        """
        sources = self.get_news_sources(ally)

        if len(sources) == 0:
            ally.say(
                "You have not configured any source. Getting top headlines\n",
                Fore.GREEN)
            url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=" + \
                self.get_api_key(ally)
        else:
            url = "https://newsapi.org/v2/top-headlines?sources="
            for source in sources:
                url += source + ","
            url += "&apiKey=" + self.get_api_key(ally)
        return self._get(ally, url)

    def get_news(self, ally, searchlist):
        """
            gets top news based on a particular search list , based on the news channel of the user (if it exists)
        """
        sources = self.get_news_sources(ally)

        url = "https://newsapi.org/v2/everything?q="

        for i in searchlist:
            url += i + "%20"
        if len(sources) != 0:
            url += "&sources="
            for source in sources:
                url += source + ","
        url += "&apiKey=" + self.get_api_key(ally)
        return self._get(ally, url)

    def _get(self, ally, url):
        """fetch a webpage"""
        response = requests.get(url)
        if response.status_code == requests.codes.ok:
            data = json.loads(response.text)
            return data
        else:
            if response.status_code == 401:
                ally.say("API key not valid", Fore.RED)
            else:
                ally.say("An error occured: Error code: "
                           + response.raise_for_status(), Fore.RED)
            return None

    def parse_articles(self, data, ally):
        article_list = {}
        index = 1
        if data is None:
            ally.say("No Articles", Fore.RED)
            return
        # ally.say articles with their index
        if not data['articles']:
            ally.say("No Articles matching the word(s)", Fore.RED)
            return
        for article in data['articles']:
            ally.say(str(index) + ": " + article['title'])
            article_list[index] = article
            index += 1

        # Attribution link for News API to comply with TOU
        ally.say("\nPowered by News API. Type NewsAPI to learn more")
        ally.say("\nType index to expand news, 0 to return to ally prompt\n")

        # Check to see if index or NewsAPI was enterd
        idx = ally.input()
        if idx.lower() == "newsapi":
            webbrowser.open('https://newsapi.org/')
            return

        # check if we have a valid index
        try:
            int(idx)
            if int(idx) > (index - 1):
                ally.say(str(idx) + " is not a valid index", Fore.RED)
                return
            elif int(idx) == 0:
                return
        except ValueError:
            ally.say("Not a valid index", Fore.RED)
            return

        # if index valid ally.say article description
        ally.say(article_list[int(idx)]['description'])

        ally.say("Do you want to read more? (yes/no): ")
        i = ally.input()
        # if user wants to read more open browser to article url
        if i.lower() == "yes" or i.lower() == 'y':
            webbrowser.open(article_list[int(idx)]['url'])
        return
