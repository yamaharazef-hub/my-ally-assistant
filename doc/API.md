# CmdInterpreter

# AllyAPI
```python
AllyAPI(self, ally)
```

Ally interface for plugins.

Plugins will receive a instance of this as the second (non-self) parameter
of the exec()-method.

Everything Ally-related that can't be implemented as a stateless-function
in the utilities-package should be implemented here.

## say
```python
AllyAPI.say(self, text, color='', speak=True)
```

This method give the ally the ability to print a text
and talk when sound is enable.
:param text: the text to print (or talk)
:param color: for text - use colorama (https://pypi.org/project/colorama/)
              e.g. Fore.BLUE
:param speak: False, if text shouldn't be spoken even if speech is enabled

## input
```python
AllyAPI.input(self, prompt='', color='')
```

Get user input

## input_number
```python
AllyAPI.input_number(self, prompt='', color='', rtype=<class 'float'>, rmin=None, rmax=None)
```

Get user input: As number.

Guaranteed only returns number - ask user till correct number entered.

:param prompt: Printed to console
:param color: Color of prompot
:param rtype: type of return value; e.g. float (default) or int
:param rmin: Minum of values returned
:param rmax: Maximum of values returned

## connection_error
```python
AllyAPI.connection_error(self)
```
Print generic connection error
## exit
```python
AllyAPI.exit(self)
```
Immediately exit Ally
## notification
```python
AllyAPI.notification(self, msg, time_seconds=0)
```

Sends notification msg in time_in milliseconds
:param msg: Message. Either String (message body) or tuple (headline, message body)
:param time_seconds: Time in seconds to wait before showing notification

## schedule
```python
AllyAPI.schedule(self, time_seconds, function, *args)
```

Schedules function
After time_seconds call function with these parameter:
   - reference to this AllyAPI instance
   - schedule_id (return value of this function)
   - *args
:return: integer, id - use with cancel

## cancel
```python
AllyAPI.cancel(self, schedule_id)
```

Cancel event scheduled with schedule
:param schedule_id: id returned by schedule

## enable_voice
```python
AllyAPI.enable_voice(self)
```

Use text to speech for every text passed to ally.say()

## disable_voice
```python
AllyAPI.disable_voice(self)
```

Stop text to speech output for every text passed to ally.say()

## is_voice_enabled
```python
AllyAPI.is_voice_enabled(self)
```

Returns True/False if voice is enabled/disabled with
enable_voice or disable_voice
Default: False (disabled)

## get_data
```python
AllyAPI.get_data(self, key)
```

Get a specific key from memory

## add_data
```python
AllyAPI.add_data(self, key, value)
```

Add a key and value to memory

## update_data
```python
AllyAPI.update_data(self, key, value)
```

Updates a key with supplied value.

## del_data
```python
AllyAPI.del_data(self, key)
```

Delete a key from memory

## eval
```python
AllyAPI.eval(self, s)
```

Simulates typing 's' in Ally prompt

