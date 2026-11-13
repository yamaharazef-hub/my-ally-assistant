"""
This plugin generates curl request for the user. The user needs to specify the parameters
HTTP Method, Content Type, Data, Endpoint. The output is the curl request.
The plugin also validates the user input before generating the curl output.
"""


from plugin import plugin
import json
from colorama import Fore


@plugin("generate curl")
class GenerateCurl(object):

    def __call__(self, ally, s):
        self._input_params = {}
        self._collect_parameters(ally)
        self._validate_parameters(ally)
        self._generate_curl_request(ally)

    def _collect_parameters(self, ally):
        http_method = ally.input(prompt="HTTP Method: ", color=Fore.BLUE)
        ally.say(text="Select Content Type\n\n1. JSON\n2. No Data\n")
        content_type = ally.input_number(
            prompt="Enter your choice: ", 
            color=Fore.BLUE, 
            rtype=int, 
            rmin=1, 
            rmax=2
        )
        data = ally.input(prompt="Enter / copy the data: ", color=Fore.BLUE)
        endpoint = ally.input(prompt="Specify the HTTP endpoint: ", color=Fore.BLUE)

        self._input_params = {
            "method": http_method.upper(),
            "content_type": content_type,
            "data": data,
            "endpoint": endpoint
        }

    def _validate_parameters(self, ally):

        if "method" not in self._input_params:
            ally.say(text="HTTP Method missing.", color=Fore.RED)
            ally.exit()

        if "content_type" not in self._input_params:
            ally.say(text="Content Type missing.", color=Fore.RED)
            ally.exit()

        if "data" not in self._input_params:
            ally.say(text="Data missing. Could be empty but should be present.", color=Fore.RED)
            ally.exit()

        if "endpoint" not in self._input_params:
            ally.say(text="Endpoint missing.", color=Fore.RED)
            ally.exit()

        if self._valid_method(ally) and self._valid_content_type(ally) and \
           self._valid_data(ally) and self._valid_endpoint(ally):
            pass
        else:
            ally.exit()

    def _valid_method(self, ally):

        valid_methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]

        if self._input_params["method"] not in valid_methods:
            ally.say(text="Invalid HTTP method provided.", color=Fore.RED)
            return False
        return True

    def _valid_content_type(self, ally):
        return True

    def _valid_data(self, ally):

        data = self._input_params["data"]
        content_type = self._input_params["content_type"]

        if content_type == 2:
            return True

        if content_type == 1:
            try:
                json.loads(data)
                return True
            except ValueError as e:
                ally.say(text="Invalid data format based on content type.", color=Fore.RED)
                return False

    def _valid_endpoint(self, ally):
        return True

    def _generate_curl_request(self, ally):

        curl_string = "curl "

        curl_string += "-X{} ".format(self._input_params["method"])

        if self._input_params["content_type"] == 1:
            curl_string += '-H "Content-type: application/json" '

        if self._input_params["content_type"] != 2:
            curl_string += " -d '{}'".format(self._input_params["data"])

        curl_string += " '{}'".format(self._input_params["endpoint"])
        ally.say(text=curl_string, color=Fore.GREEN)
