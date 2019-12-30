import logging

from .node import Node

class Data(Node):
    """
    Data is abstraction of a file or set of files on disk. Mainly it's just a container of
    a Match object, with a small amount of functionality to exist as output and/or input
    of WorkFiles. 
    
    The Data should be considered version-less, as which version to pick up
    is decided by a Process. 
    
    A Data object can also exist without any versions on disk yet.
    """
    def __init__(self, match):
        """
        Match object is navigator match object
        Parent is Output from a workfile. Can be None to support data types not supported
        in the UI yet.
        """
        super(Data, self).__init__(match)
        self._match = match

    def getMatch(self):
        """
        Returns deepcopy of Navigator Match object, which can be used to query versions
        on disk or generate paths to new versions
        """
        return copy.deepCopy(self._match)

