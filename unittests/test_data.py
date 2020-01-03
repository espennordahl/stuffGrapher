import unittest

from core import Data
from core.attributes import *

class TestCreate(unittest.TestCase):
    def test_demo(self):
        tmp = "foo"

    def test_compare(self):
        obj1 = Data("foo")
        obj2 = Data("foo")
        obj3 = Data("bar")
        obj4 = Data("bar")
        obj4.addAttribute(BoolAttribute("testAttr", True))
        self.assertEqual(obj1, obj2)
        self.assertNotEqual(obj1, obj3)
        self.assertNotEqual(obj3, obj4)
