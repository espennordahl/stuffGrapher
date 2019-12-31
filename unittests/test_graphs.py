import unittest

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

class TestSerialize(unittest.TestCase):
    def test_simple(self):
        graph = Graph()


if __name__ == '__main__':
    unittest.main()

