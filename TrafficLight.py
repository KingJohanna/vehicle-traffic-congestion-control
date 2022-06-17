import numpy as np

class SimpleTrafficLight:
    def __init__(self):
        """
        T : float
            The period of the on/off-sequence.
        time_delay : float
            The time delay of the sequence. At default (0), the traffic light is at service for a time of T/2.
        """
        self.T = 0
        self.time_delay = 0
        
    def initialize(self, T: float, time_delay: float) -> None:
        """
        Initializes the SimpleTrafficLight instance.
        
        T : float
            The period of the on/off-sequence.
        time_delay : float
            The time delay of the sequence.
        """
        self.T = T
        self.time_delay = time_delay
        
    def saturation_rate(self, t: float) -> float:
        """
        Returns the saturation rate at a given time.
        
        t : float
            The current time [s]. 
        """
        if np.sin(2*np.pi*(t-self.time_delay)/self.T) > 0:
            return 1
        else:
            return 0