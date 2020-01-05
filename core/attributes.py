import logging

class Attribute:
    def __init__(self, key, value=None):
        if isinstance(key, str):
            self.key = str(key)
        else:
            logging.error("Attribute names must be strings. Received: " + type(key))
        self.value = value

    @classmethod
    def deserialize(self):
        

    def serialize(self):
        root = {}
        root["class"] = self.__class__.__name__
        root["key"] = self.key
        root["value"] = str(self.value)
        return root

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value

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

