from abc import ABC, abstractmethod


class BaseAgent(ABC):

    """
    Base class for all RCA agents.
    """


    def __init__(self, name):

        self.name = name



    @abstractmethod
    def analyze(self, context):

        pass