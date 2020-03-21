import unittest

from core.project import Project



class TestProject(unittest.TestCase):
    def test_serialization(self):
        project = Project()
        json = project.serialize()
        project2 = Project.deserialize(json)
        self.assertEqual(project, project2)
