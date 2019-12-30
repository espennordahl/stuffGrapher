import unittest

from core.actions import *
from core.scenefiles import *

class TestActions(unittest.TestCase):
    def test_constructors(self):
        action = RenderAction(MayaFile("lighting"))
        action = ComprenderAction(NukeFile("comp"))
        action = PublishGeoAction(MayaFile("model"))
        action = PublishGeocacheAction(MayaFile("anim"))
        action = PublishLookdevAction(HoudiniFile("lookdev"))

    def test_parent(self):
        tmp = "foo"
