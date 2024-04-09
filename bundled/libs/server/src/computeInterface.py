from dataclasses import dataclass, field

@dataclass
class ComputeData:

    message: str
    system: str
    isComplete: bool = True

    def __init___(self, message: str, system: str, isComplete: bool):
        self.message = message
        self.system = system
        self.isComplete = isComplete
