import json
import logging

from .shot import Shot

class Project:
    """
    Container for an entire project.
    """
    def __init__(self, name="", shots={}, templates={}, filename=""):
        self.name = name
        self.shots = shots
        self.templates = templates
        self.filename = filename

    def addShot(self, shot):
        ##TODO: Introspection
        self.shots[shot.name] = shot

    def addTemplate(self, template):
        ##TODO: Introspection
        self.templates[template.name] = template

    def serialize(self):
        root = {}

        root["class"] = self.__class__.__name__

        root["name"] = self.name
        
        root["shots"] = {}
        for shotname in self.shots:
            root["shots"][shotname] = self.shots[shotname].serialize()

        root["templates"] = {}
        for templatename in self.templates:
            root["templates"][templatename] = self.templates[templatename].serialize()

        root["filename"] = self.filename

        return root

    @classmethod
    def deserialize(cls, root):
        if root["class"] != "Project":
            logger.error("Wrong deserializer called: " + root["class"])
        
        name = root["name"]
        filename = root["filename"]

        project = Project(name=name, filename=filename)

        templateData = root["templates"]
        for data in templateData.values():
            project.addTemplate(Shot.deserialize(data))

        shotData = root["shots"]
        for data in shotData.values():
            shot = Shot.deserialize(data)
            if data["parent"]:
                shot.parent = project.templates[data["parent"]["name"]]
            project.addShot(shot)

        return project


    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.name != other.name:
            return False

        if self.filename != other.filename:
            return False

        if self.shots != other.shots:
            return False

        if self.templates != other.templates:
            return False

        return True

