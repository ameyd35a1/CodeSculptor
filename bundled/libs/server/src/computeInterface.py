from dataclasses import dataclass, field

@dataclass
class ComputeData:

    message: str
    system: str
    isComplete: bool = True
    maxTokens: int = 1024

    def __init___(self, message: str, system: str, isComplete: bool, maxTokens: int):
        self.message = message
        self.system = system
        self.isComplete = isComplete
        self.maxTokens = maxTokens
