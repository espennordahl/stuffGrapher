import unittest

from core import Graph
from core.actions import RenderAction
from core.scenefiles import MayaFile

class TestCreate(unittest.TestCase):
    def test_create_demo(self):
        workfile = MayaFile("anim")

    def test_create_graph(self):
        graph = Graph()

        scenefile = MayaFile("lighting")
        graph.addNode(scenefile)

        action = RenderAction(scenefile)

        data = action.createRenderLayer("dragon")

        self.assertEqual(len(graph.nodes), 3)

if __name__ == '__main__':
    unittest.main()

