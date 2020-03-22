import unittest
import json

from random import random, choice

from core import Graph

class TestCreate(unittest.TestCase):
    def test_create_demo(self):
        self.assertEqual(1+1, 2)

    def test_create_graph(self):
        graph = Graph()
        scenefile = graph.createNode("MayaFile", "lighting")
        action = graph.createNode("RenderAction", "dragon")
        data = graph.createNode("Data", "dragon")

        self.assertEqual(len(graph.nodes), 3)

    def test_lots_of_nodes(self):
        graph = Graph()
        actions = ["RenderAction", "ComprenderAction"]
        scenefiles = ["MayaFile", "NukeFile", "HoudiniFile"]

        nodes = {}
        nodes["scenes"] = []
        nodes["actions"] = []

        numNodes = 2000
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

        self.assertEqual(len(nodes["actions"]) + len(nodes["scenes"]), numNodes)
        self.assertEqual(len(graph.nodes), numNodes)
        for nodename in graph.nodes:
            self.assertEqual(nodename, graph.nodes[nodename].name)

        json1 = graph.serialize()
        self.assertTrue(json.dumps(json1))
        revivedGraph = Graph.deserialize(json1)
        self.assertEqual(graph, revivedGraph)

    def test_node_names(self):
        graph = Graph()
        scenefile = graph.createNode("MayaFile", "lighting")
        action = scenefile.createAction("RenderAction", "dragon")
        data = action.createData("RenderData")

        self.assertEqual(scenefile.name, "MayaFile")
        self.assertEqual(action.name, "RenderAction")
        self.assertEqual(data.name, "RenderData")

    def foo(self):
        self.assertEqual(1, 2)

if __name__ == '__main__':
    unittest.main()

