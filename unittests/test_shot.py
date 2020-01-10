import unittest

from random import random, choice

from core import Shot
from core import Graph

class TestShot(unittest.TestCase):
    def test_constructor(self):
        shot = Shot("fx010")

    def createGraph(self):
        graph = Graph()
        actions = ["RenderAction", "ComprenderAction"]
        scenefiles = ["MayaFile", "NukeFile", "HoudiniFile"]

        nodes = {}
        nodes["scenes"] = []
        nodes["actions"] = []

        numNodes = 100
        for x in range(0,numNodes):
            r = random()
            if nodes["scenes"] and r > 0.5:
                scene = choice(nodes["scenes"])
                actiontype = choice(scene.knownActions())
                node = scene.createAction(actiontype, "bar")
                nodes["actions"].append(node)
            else:
                node = graph.createNode(choice(scenefiles), "foo")
                nodes["scenes"].append(node)

        return graph

    def test_serialize(self):
        shots = []
        
        parent = Shot("fx000")
        parent.graph = self.createGraph()
        shots.append(parent)

        for shotname in ["fx010", "fx020", "fx030"]:
            shot = Shot(shotname)
            shot.parent = parent.name
            shots.append(shot)

        for shotname in ["ab010", "ab020", "ab030", "ab040", "ab050"]:
            shot = Shot(shotname)
            shot.graph = self.createGraph()
            shots.append(shot)

        for shot in shots:
            json = shot.serialize()
            self.assertEqual(Shot.deserialize(json), shot)
