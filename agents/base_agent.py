from abc import ABC, abstractmethod

class BaseAgent(ABC):

    def __init__(self, name, llm_client, retriever=None):
        self.name = name
        self.llm_client = llm_client
        self.retriever = retriever

    @abstractmethod
    async def handle(self, query):
        pass