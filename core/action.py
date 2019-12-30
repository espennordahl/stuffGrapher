import logging

from .node import Node

class Action(Node):
    def __init__(self, match):
        super(Action, self).__init__(match)
