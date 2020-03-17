import sys
import copy

import logging

logger = logging.getLogger(__name__)

class Attribute:
    def __init__(self, key, value=None, parent=None, hidden=False):
        if isinstance(key, str):
            self.key = str(key)
        else:
            logger.error("Attribute names must be strings. Received: " + type(key))
        if isinstance(parent, (bool, str, float, int, list, tuple)):
            logger.error("Parent can't be of type: {}".format(type(parent)))
            raise Exception
        self.parent = parent
        self.value = value
        self.hidden = hidden

    @classmethod
    def deserialize(self, root):
        classname = root["class"]
        if not classname in dir(sys.modules[__name__]):
            logger.error("Asked to deserialize unknown class: " + classname)
        
        if classname == self.__class__.__name__:
            logger.error("Asked to serialize Attribute, which is an abstract class")

        cls = getattr(sys.modules[__name__], classname)
        obj = cls.deserialize(root)
        return obj

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        if parent == "None":
            self._parent = None
        else:
            self._parent = parent

    def parentName(self):
        if self.parent:
            return self.parent.name
        else:
            return "None"

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        logger.debug("{}.{} = {}".format(self.parentName(), self.key, value))
        self._value = value

    def setValue(self, value):
        """
        This feels like we're doublign up on the setter, but
        we need a slot to connect to in UI code, sooo..
        """
        self.value = value

    def serialize(self):
        root = {}
        root["class"] = self.__class__.__name__
        root["key"] = self.key
        root["value"] = self.value
        root["hidden"] = self.hidden
        root["parent"] = self.parent
        return root

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.key != other.key:
            return False
        if self.parentName() != other.parentName():
            return False
        if self.hidden != other.hidden:
            return False
        if hasattr(self.value, "attributes"):
            ## This feels a little dirty, but if we don't do this,
            ## we cause an infinite recursion
            return self.value.name == other.value.name
        else:
            return self.value == other.value

    def __repr__(self):
        if isinstance(self.value, Attribute):
            return "Parent:{} Key:{} Value:{}".format(self.parentName(), self.key, str(self.value.key))
        else:
            return "Parent:{} Key:{} Value:{}".format(self.parentName(), self.key, str(self.value))

class BoolAttribute(Attribute):
    def __init__(self, key, value=None, parent=None, hidden=False):
        super(BoolAttribute, self).__init__(key=key, value=value, parent=parent, hidden=hidden)

    @classmethod
    def deserialize(self, root):
        obj = BoolAttribute(root["key"], 
                                value=bool(root["value"]), 
                                hidden=root["hidden"])
        return obj

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not isinstance(value, bool):
            logger.error("Expected Bool, got {}".format(type(value)))
            raise Exception
            return
        logger.debug("{}.{} = {}".format(self.parentName(), self.key, value))
        self._value = value

class ColorAttribute(Attribute):
    def __init__(self, key, value=None, parent=None, hidden=False):
        super(ColorAttribute, self).__init__(key=key, value=value, parent=parent, hidden=hidden)

class EnumAttribute(Attribute):
    def __init__(self, key, elements=[], value=None, parent=None, hidden=False):
        self.elements = copy.copy(elements)
        if len(self.elements):
            self._value = 0
        else:
            self._value = None
        super(EnumAttribute, self).__init__(key=key, parent=parent, hidden=hidden)

    def addElement(self, element):
        self.elements.append(element)
        if self._value == None:
            self.value = self.elements.index(element)

    def removeElement(self, element):
        self.elements.remove(element)

    @property
    def value(self):
        if self.elements and self._value != None:
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
                return
            else:
                self._value = value
        else:
            if value not in self.elements:
                logging.warning("Enum value must be in elements")
                return
            else:
                self._value = self.elements.index(value)
        logger.debug("{}.{} = {}".format(self.parentName(), self.key, value))

    @classmethod
    def deserialize(self, root):
        key = root["key"]
        elements = root["elements"]
        value = root["value"]
        hidden = root["hidden"]
        obj = EnumAttribute(key=key, elements=elements, value=value, hidden=hidden)
        obj.value = value
        return obj

    def serialize(self):
        root = super(EnumAttribute, self).serialize()

        root["elements"] = self.elements
        root["value"] = self._value
        
        return root

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if self.key != other.key:
            return False
        if self.value != other.value:
            return False
        if self.elements != other.elements:
            return False
        if self.hidden != other.hidden:
            return False
        return True

class FloatAttribute(Attribute):
    def __init__(self, name, value=None, parent=None, hidden=False):
        super(FloatAttribute, self).__init__(name, value, parent, hidden)

    @classmethod
    def deserialize(self, root):
        obj = FloatAttribute(root["key"], 
                                value=root["value"],
                                hidden=root["hidden"])
        return obj

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not isinstance(value, (float, int)):
            logger.error("Expected number, got {}".format(type(value)))
            raise Exception
            return
        logger.debug("{}.{} = {}".format(self.parentName(), self.key, value))
        self._value = value


class StringAttribute(Attribute):
    def __init__(self, name, value=None, parent=None, hidden=False):
        super(StringAttribute, self).__init__(name, value, parent, hidden)

    @classmethod
    def deserialize(self, root):
        obj = StringAttribute(root["key"], 
                                value=str(root["value"]),
                                hidden=root["hidden"])
        return obj

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not isinstance(value, str):
            logger.error("Expected String, got {}".format(type(value)))
            raise Exception
            return
        logger.debug("{}.{} = {}".format(self.parentName(), self.key, value))
        self._value = value


class InputAttribute(Attribute):
    def __init__(self, name, value=None, parent=None, hidden=False):
        super(InputAttribute, self).__init__(name, value, parent, hidden)
        self._connectionCallback = None

    @classmethod
    def deserialize(self, root):
        value = root["value"]
        hidden = root["hidden"]
        if value == None:
            obj = InputAttribute(root["key"], None, hidden=hidden)
        else:
            obj = InputAttribute(root["key"], str(value), hidden=hidden)
        return obj

    def serialize(self):
        root = {}
        root["class"] = self.__class__.__name__
        root["key"] = self.key
        root["hidden"] = self.hidden
        root["parent"] = self.parent
        if self.value:
            root["value"] = str(self.value.name)
        else:
            root["value"] = None
        return root

    def setConnectionCallback(self, callback):
        self._connectionCallback = callback

    def isLegalConnection(self, connection):
        logger.debug("Checking connection legality")
        if not isinstance(connection, OutputAttribute):
            return False
        logger.debug("Connection callback: {}".format(self._connectionCallback))
        if callable(self._connectionCallback):
            return self._connectionCallback(connection)
        ## Default to all connections being legal
        return True

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        from core import Node
        if not isinstance(value, (Node, str, type(None))):
            logger.error("Expected Node, string or None, got {}".format(type(value)))
            raise Exception
            return
        logger.debug("{}.{} = {}".format(self.parentName(), self.key, value))
        self._value = value


class ArrayInputAttribute(InputAttribute):
    def __init__(self, key, value=None, parent=None, hidden=False):
        super(ArrayInputAttribute, self).__init__(key=key, value=value, parent=parent, hidden=hidden)

class OutputAttribute(Attribute):
    def __init__(self, key, value=None, parent=None, hidden=False):
        super(OutputAttribute, self).__init__(key=key, value=value, parent=parent, hidden=hidden)

    @classmethod
    def deserialize(self, root):
        hidden = root["hidden"]
        value = root["value"]
        obj = OutputAttribute(root["key"], value=value, hidden=hidden)
        return obj

    def serialize(self):
        root = {}
        root["class"] = self.__class__.__name__
        root["key"] = self.key
        root["hidden"] = self.hidden
        if self.value:
            root["value"] = str(self.value.name)
        else:
            root["value"] = None
        return root

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        from core import Node
        if not isinstance(value, (Node, str, type(None))):
            logger.error("Expected Node, string or None, got {}".format(type(value)))
            raise Exception
            return
        logger.debug("{}.{} = {}".format(self.parentName(), self.key, value))
        self._value = value


