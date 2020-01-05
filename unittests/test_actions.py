import unittest

from core.actions import *
from core.scenefiles import *
from core.attributes import *
from core import Action

class TestActions(unittest.TestCase):
    def createActions(self):
        actions = []
        actions.append(RenderAction("foo"))
        actions.append(ComprenderAction("foo"))
        actions.append(PublishGeoAction("foo"))
        actions.append(PublishGeocacheAction("foo"))
        actions.append(PublishLookdevAction("foo"))
        return actions 

    def test_constructors(self):
        self.createActions()

    def test_render(self):
        scene = MayaFile("lighting")
        action = scene.createAction("RenderAction", "dragon")
        
        updateAttr = action.attributes["updateResources"]
        self.assertIsInstance(updateAttr, BoolAttribute)
        self.assertTrue(updateAttr.value)

        sceneAttr = action.attributes["scenefile"]
        self.assertIsInstance(sceneAttr, InputAttribute)
        self.assertIs(sceneAttr.value, scene)


    def test_serialize(self):
        for obj1 in self.createActions():
            json1 = obj1.serialize()
            obj2 = Action.deserialize(json1)
            self.assertEqual(obj1, obj2)
