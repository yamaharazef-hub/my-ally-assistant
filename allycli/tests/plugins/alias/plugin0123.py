from plugin import Plugin


class Plugin0(Plugin):
    """Test"""

    def require(self):
        pass

    def complete(self):
        pass

    def alias(self):
        yield "Plugin1"
        yield "Plugin2"

    def run(self, ally, s):
        pass


class Plugin3(Plugin):
    """Test"""

    def require(self):
        pass

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, ally, s):
        pass
