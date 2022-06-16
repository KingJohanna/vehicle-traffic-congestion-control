import numpy as np

class SimpleTrafficLight:
    def __init__(self):
        self.T = 0
        self.time_delay = 0
        
    def initialize(self, T: float, time_delay: float) -> None:
        self.T = T
        self.time_delay = time_delay
        
    def saturation_rate(self, t: float) -> float:
        if np.sin(2*np.pi*(t-self.time_delay)/self.T) > 0:
            return 1
        else:
            return 0