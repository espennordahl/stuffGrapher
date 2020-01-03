import unittest

from random import random, choice

from core import Graph

class TestCreate(unittest.TestCase):
    def test_create_demo(self):
        self.assertEqual(1+1, 2)

    def test_create_graph(self):
        graph = Graph()
        scenefile = graph.createSceneFile("MayaFile", "lighting")
        action = graph.createAction("RenderAction", scenefile)
        data = action.createRenderLayer("dragon")

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
                node = graph.createAction(choice(actions), choice(nodes["scenes"]))
                nodes["actions"].append(node)
            else:
                node = graph.createSceneFile(choice(scenefiles), "foo")
                nodes["scenes"].append(node)

        self.assertEqual(len(nodes["actions"]) + len(nodes["scenes"]), numNodes)
        self.assertEqual(len(graph.nodes), numNodes)
        for nodename in graph.nodes:
            self.assertEqual(nodename, graph.nodes[nodename].name)

    def test_node_names(self):
        graph = Graph()
        scenefile = graph.createSceneFile("MayaFile", "lighting")
        action = graph.createAction("RenderAction", scenefile)
        data = action.createRenderLayer("dragon")

        self.assertEqual(scenefile.name, "MayaFile")
        self.assertEqual(action.name, "RenderAction")
        self.assertEqual(data.name, "RenderLayer")

class TestSerialize(unittest.TestCase):
    def test_simple(self):
        graph = Graph()


if __name__ == '__main__':
    unittest.main()

