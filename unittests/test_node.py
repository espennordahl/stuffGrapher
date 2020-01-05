import unittest

from core import Node
from core.attributes import *

class TestCreate(unittest.TestCase):
    def test_demo(self):
        tmp = "foo"

    def test_compare(self):
        obj1 = Node("foo")
        obj2 = Node("foo")
        obj3 = Node("bar")
        obj4 = Node("bar")
        obj4.addAttribute(BoolAttribute("testAttr", True))
        self.assertEqual(obj1, obj2)
        self.assertNotEqual(obj1, obj3)
        self.assertNotEqual(obj3, obj4)

    def test_serialize(self):
        obj1 = Node("foo")
        obj1.addAttribute(BoolAttribute("testAttr", True))
        obj1.addAttribute(StringAttribute("foo", "bar"))
        json1 = obj1.serialize()
        obj2 = Node.deserialize(json1)
        self.assertEqual(obj1, obj2)
