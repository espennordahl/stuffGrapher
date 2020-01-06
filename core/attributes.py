import sys

import logging

class Attribute:
    def __init__(self, key, value=None):
        if isinstance(key, str):
            self.key = str(key)
        else:
            logging.error("Attribute names must be strings. Received: " + type(key))
        self.value = value

    @classmethod
    def deserialize(self, root):
        classname = root["class"]
        if not classname in dir(sys.modules[__name__]):
            logging.error("Asked to deserialize unknown class: " + classname)
        
        if classname == self.__class__.__name__:
            logging.error("Asked to serialize Attribute, which is an abstract class")

        cls = getattr(sys.modules[__name__], classname)
        obj = cls.deserialize(root)
        return obj
            

    def serialize(self):
        root = {}
        root["class"] = self.__class__.__name__
        root["key"] = self.key
        root["value"] = str(self.value)
        return root

    def __eq__(self, other):
    	if not isinstance(other, self.__class__):
    		return False
    	return self.key == other.key and self.value == other.value

class BoolAttribute(Attribute):
    def __init__(self, name, value=None):
        super(BoolAttribute, self).__init__(name, value)

    @classmethod
    def deserialize(self, root):
        obj = BoolAttribute(root["key"], bool(root["value"]))
        return obj

class ColorAttribute(Attribute):
    def __init__(self, name, value=None):
        super(ColorAttribute, self).__init__(name, value)


class StringAttribute(Attribute):
    def __init__(self, name, value=None):
        super(StringAttribute, self).__init__(name, value)

    @classmethod
    def deserialize(self, root):
        obj = StringAttribute(root["key"], str(root["value"]))
        return obj

class InputAttribute(Attribute):
    def __init__(self, name, value=None):
        super(InputAttribute, self).__init__(name, value)

    @classmethod
    def deserialize(self, root):
        value = root["value"]
        if value == None:
            obj = InputAttribute(root["key"], None)
        else:
            obj = InputAttribute(root["key"], str(value))
        return obj

    def serialize(self):
        root = {}
        root["class"] = self.__class__.__name__
        root["key"] = self.key
        if self.value:
            root["value"] = str(self.value.name)
        else:
            root["value"] = None
        return root


