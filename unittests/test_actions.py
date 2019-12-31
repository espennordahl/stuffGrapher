import unittest

from core.actions import *
from core.scenefiles import *
from core.attributes import *

class TestActions(unittest.TestCase):
    def test_constructors(self):
        action = RenderAction(MayaFile("lighting"))
        action = ComprenderAction(NukeFile("comp"))
        action = PublishGeoAction(MayaFile("model"))
        action = PublishGeocacheAction(MayaFile("anim"))
        action = PublishLookdevAction(HoudiniFile("lookdev"))

    def test_render(self):
        scene = MayaFile("lighting")
        action = RenderAction(scene)
        
        updateAttr = action.attributes["updateResources"]
        self.assertIsInstance(updateAttr, BoolAttribute)
        self.assertTrue(updateAttr.value)

        sceneAttr = action.attributes["scenefile"]
        self.assertIsInstance(sceneAttr, InputAttribute)
        self.assertIs(sceneAttr.value, scene)
