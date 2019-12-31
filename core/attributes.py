import logging

class Attribute:
    def __init__(self, name, value=None):
        if isinstance(name, str):
            self.name = str(name)
        else:
            logging.error("Attribute names must be strings. Received: " + type(name))
        self.value = value

class BoolAttribute(Attribute):
    def __init__(self, name, value=None):
        super(BoolAttribute, self).__init__(name, value)

class ColorAttribute(Attribute):
    def __init__(self, name, value=None):
        super(ColorAttribute, self).__init__(name, value)

class StringAttribute(Attribute):
    def __init__(self, name, value=None):
        super(StringAttribute, self).__init__(name, value)

class InputAttribute(Attribute):
    def __init__(self, name, value=None):
        super(InputAttribute, self).__init__(name, value)

class OutputAttribute(Attribute):
    def __init__(self, name, value=None):
        super(OutputAttribute, self).__init__(name, value)

