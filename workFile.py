import logging

class WorkFile:
    """
    Scene file used to consume and create data. Typical examples are Maya scenes, 
    Nuke scripts etc. 

    WorkFiles should be considered version-less, as which version to pick up is
    decided by a Process
    
    A WorkFile object can also exist without any versions on disk yet.
    """
    def __init__(self, match):
        """
        Takes a Navigator Match object
        """
        self._match = match
        self._attributes = []
        self._inputs = []
        self._outputs = []

    def getMatch(self):
        """
        Returns deepcopy of Navigator Match object, which can be used to query versions
        on disk or generate paths to new versions
        """  
        return copy.deepCopy(self._match)

    def addAttribute(self, attribute):
        """
        Adds an Attribute to the WorkFile. 
        
        Note that an attribute can only be added once
        """
        if isinstance(attribute, Attribute):
            if attribute in self._attributes:
                logging.warning("Attribute is already on Node. Skipping: " + attribute)
                return
            self._attributes.append(attribute)
        else:
            logging.error("Object is not an Attribute object. Skipping: " + attribute)

    def getAttributes(self):
        """
        Returns a reference to the attributes on the WorkFile.
        """
        return self._attributes

    def removeAttribute(self, attribute):
        """
        Removes all copies of the attribute from the WorkFile
        """
        if attribute in self,_attributes:
            self._attributes.remove(attribute)
        else:
            logging.warning("Tried to remove unexisting attribute: " + attribute)

    def addInput(self, input):
        """

        """
        if isinstance(input, Data):
            self._inputs.append(input)
        else:
            logging.error("Object is not a Data object. Skipping: " input)

    def getInputs(self):
        return self._inputs

    def removeInput(self, input):
        if input in self._inputs:
            self._inputs.remove(input)
        else:
            logging.warning("Tried to remove unexisting input: " + input)

    def addOutput(self, output):
        if isinstance(output, Output):
            if output in self._outputs:
                logging.warning("Output is already on Node. Skipping: " + output)
                return
            self._outputs.append(output)
        else:
            logging.error("Object is not Output object. Skipping: " + output)

    def getOutputs(self):
        return self.outputs

    def removeOutput(self, outputs):
        if output in self._outputs:
            self._outputs.remove(output)
        else:
            logging.warning("Tried to remove unexisting output: " + output)

