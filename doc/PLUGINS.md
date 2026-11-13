# Plugins

## Basic
```
from plugin import plugin

@plugin("hello world")
def hello_world(ally, s):
    """Prints \"hello world!\""""
    ally.say("Hello World!")
```

Or use "callable" class:

```
from plugin import plugin

@plugin("hello world")
class hello_world:
    """Prints \"hello world!\""""
    def __call__(self, ally, s):
        ally.say("Hello World!")
```


## Run-Parameter

* 1: ally -> instance of CmdInterpreter.AllyAPI. Click [here](API.md).
* 2: s -> string; what the user entered

## Location

Plugins are searched for in two locations:

* custom - for your own plugins
* allycli/plugins - for pre-installed plugins

It is fine to develop and test plugins in the custom-folder, but before submitting always move them to allycli/plugins.


## Features

Plugins may be modified using the decorators @alias, @require and @complete.

These special decorators may be used in any order or several times.

Note that @plugin always **must** be declared last.


### Alias

Example:

```
from plugin import plugin, alias


@alias("Hello", "Hi")
@plugin("helloworld")
def helloWorld(ally, s):
   (...)
```

This would alias "HelloWorld" to "Hello" and "Hi".

An Alias behaves just like copy-pasting the whole plugin with a new name.

### Require

Not all plugins are compatible with every system. To specify compatibility constraints, use the require-feature.

Plugins, which are non compatible are ignored and will not be displayed.

Current available requirements:

* Network: (True, False)
* Platform: (plugin.LINUX, plugin.MACOS, plugin.WINDOWS, plugin.UNIX - equals plugin.LINUX + plugin.MACOS)
* Python: (plugin.PYTHON2, plugin.PYTHON3)
* Native: (any string)

Native means any native Binary in $PATH must exist. If multiple natives are specified (unlike other requirements) ALL must be fulfilled.

Example: Only support Python 3 with Linux or Windows; Require firefox and curl with active network connection.


```
from plugin import plugin, require, PYTHON3, LINUX, WINDOWS


@require(platform=[LINUX, WINDOWS], python=PYTHON3, network=True, native=["firefox", "curl"])
@plugin("helloworld")
def helloWorld(ally, s):
    (...)
```

Special behaviour:

* If a plugin is incompatible because of missing native binary (and because of natives only), an notification shall be printed.
* If network=True is required, you won't need to try-catch requests.ConnectionError - this error is auto-cached with connection-error


### Completion

Use Completion feature (complete with TAB).

```
from plugin import plugin, complete


@complete("complete0", "complete1")
@plugin
def helloWorld(ally, s):
    (...)
```


### Multi word commands

Take "check ram" and "check weather". Of course you could create a plugin "check" and doing something like ``if 'ram' in s``. But it's better to create two separate plugins:

```
@plugin("check weather")
check_weather(ally, s):
    (...)

@alias("info ram")
@plugin("check ram")
check_ram(ally, s):
    (...)
```

Multi word commands even work with alias().


### Init

If a Class-Plugins has a method ``init(self, ally)`` this method will be called during initialisation.

```
from plugin import plugin


@plugin
class HelloWorld:
    """
    Description of Hello world
    """
    def init(self, ally):
        ally.say("INIT HelloWorld!!!")

    def require(self):
        pass

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, ally, s):
        ally.say("Hello world!")
```

##
