from plugin import plugin
import urllib.request
from colorama import Fore


@plugin("website status")
def check_website_status(ally, s):
    prompt = "Please enter a website URL: "
    while True:
        # asks for URL to check
        # adds in https or http if necessary
        url_request = str(ally.input(prompt))
        if url_request.startswith('https://'):
            pass
        elif url_request.startswith('http://'):
            pass
        else:
            url_request = 'https://' + url_request
        try:
            # tries to make a request to the URL that was input
            # uses defined headers that are not a "bot"
            headers = {}
            headers['User-Agent'] = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36")
            req = urllib.request.Request(url_request, headers=headers)
            page = urllib.request.urlopen(req)
            code = str(page.getcode())
            ally.say('The website ' + url_request +
                       ' has returned a ' + code + ' code', Fore.BLUE)
            break
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            # if there is an error it will ask if you want to try again
            ally.say(str(e), Fore.RED)
            ally.say("Make sure you are entering a valid URL")
            try_again = ally.input("Do you want to try again (y/n): ")
            try_again = try_again.lower()
            if try_again == 'y':
                continue
            else:
                break
