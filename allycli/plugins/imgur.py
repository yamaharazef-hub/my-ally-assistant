import base64
import glob
import json
import os

import requests

from plugin import plugin, require
from utilities.GeneralUtilities import IS_WIN

if IS_WIN:
    from pyreadline3 import Readline
    readline = Readline()
else:
    import readline


def complete(text, state):
    return (glob.glob(text + '*') + [None])[state]


@require(network=True)
@plugin('imgur')
def imgur(ally, s):
    """
    Uploads an image to imgur
    """

    # Autocomplete filename
    ally.say("What's the image name?: ")
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    r = readline.get_completer()
    readline.set_completer(complete)
    file = ally.input('')
    # Get the absolute path
    file = os.path.abspath(file)
    file = os.path.expanduser(file)
    if os.path.isfile(file):
        try:
            url = "https://api.imgur.com/3/image"
            headers = {"Authorization": "Client-ID 145b6ea95cf11b4"}
            # Send POST
            resp = requests.post(
                url,
                headers=headers,
                data={
                    'image': base64.b64encode(open(file, 'rb').read()),
                    'type': 'base64'
                }
            )

            objresp = json.loads(resp.text)
            # Treat response
            if objresp.get('success', False):
                ally.say('Here is your image: '
                   + str(objresp['data']['link']))
            else:
                ally.say('Error: ' + str(objresp['data']['error']))
        except requests.RequestException as e:
            ally.say(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            ally.say(f"Invalid JSON response: {str(e)}")
        except IOError as e:
            ally.say(f"File error: {str(e)}")
        except KeyError as e:
            ally.say(f"Unexpected API response format: {str(e)}")
    else:
        ally.say("No such file")

    readline.set_completer(r)
