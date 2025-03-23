import random

class Fish():
    
    def __init__(self, kind: str, length: float) -> None:
        self.kind = kind
        self.length = length
        
    def __repr__(self) -> str: return f'{self.kind}: {self.length}'
    
class FishData():
    
    def __init__(self, probability: float, min: float, max: float) -> None:
        self.probability = probability
        self.min = min
        self.max = max
        
class FishTracker():
    
    def __init__(self) -> None:
        self.record: dict[str, float] = {}
        self.fish: dict[str: FishData] = {
            'tuna':     FishData(10,   0.6,  1.40),
            'flounder': FishData(12.5, 0.15, 0.9),
            'herring':  FishData(12.5, 0.18, 0.46),
            'bass':     FishData(15,   0.25, 0.9),
            'tilapia':  FishData(15,   0.15, 0.6)
        }
        
    def log(self, fish: Fish) -> bool:
        """
        Logs the given fish in the tracker, returns true if the size is a new record
        """
        if fish.kind not in self.record: self.record[fish.kind] = 0
        bigger = fish.length > self.record[fish.kind]
        self.record[fish.kind] = max(self.record[fish.kind], fish.length)
        return bigger
    
    def get_fish(self) -> Fish:
        """
        Gets a random fish
        """
        # select the fish type
        rand = random.uniform(0, self.total_probability)
        for name, fish in self.fish.items():
            kind = name
            rand -= fish.probability
            if rand <= 0: break
        # select the size and return fish
        size = float(f'{random.uniform(self.fish[kind].min, self.fish[kind].max):.2f}')
        return Fish(kind, size)
        
    @property
    def total_probability(self) -> float: return sum([f.probability for f in self.fish.values()])