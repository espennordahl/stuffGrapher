import sys
import copy

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

class EnumAttribute(Attribute):
    def __init__(self, name, elements=[], value=None):
        self._value = None
        self.elements = copy.copy(elements)
        super(EnumAttribute, self).__init__(name, value)

    def addElement(self, element):
        self.elements.append(element)
        if self._value == None:
            self.value = self.elements.index(element)

    def removeElement(self, element):
        self.elements.remove(element)

    @property
    def value(self):
        if self.elements:
            return self.elements[self._value]
        else:
            return False

    @value.setter
    def value(self, value):
        if isinstance(value, (bool, type(None))):
            return
        elif isinstance(value, int): 
            if value >= len(self.elements):
                logging.warning("Enum index out of range")
            else:
                self._value = value
        else:
            if value not in self.elements:
                logging.warning("Enum value must be in elements")
            else:
                value = self.elements.index(value)

    @classmethod
    def deserialize(self, root):
        name = root["key"]
        elements = root["elements"]
        value = root["value"]
        obj = EnumAttribute(name, elements, value)
        return obj

    def serialize(self):
        root = {}
        root["class"] = self.__class__.__name__
        root["key"] = self.key
        root["elements"] = self.elements
        root["value"] = self._value
        return root

    def __eq__(self, other):
        if self.key != other.key:
            return False
        if self.value != other.value:
            return False
        if self.elements != other.elements:
            return False
        return True

class FloatAttribute(Attribute):
    def __init__(self, name, value=None):
        super(FloatAttribute, self).__init__(name, value)

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


