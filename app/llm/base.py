from abc import ABC, abstractmethod


class LLMAdapter(ABC):
    @abstractmethod
    def analyze(self, ticket, category, risk, examples):
        raise NotImplementedError
