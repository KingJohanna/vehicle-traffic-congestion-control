import numpy as np

class SimpleTrafficLight:
    def __init__(self):
        """
        period : float
            The period of the on/off-sequence.
        time_delay : float
            The time delay of the sequence. Light is green after after time_delay seconds has passed.
        """
        self.period = 0
        self.time_delay = 0
        
    def initialize(self, period: float, time_delay: float) -> None:
        """
        Initializes the SimpleTrafficLight instance.
        
        period : float
            The period of the on/off-sequence.
        time_delay : float
            The time delay of the sequence.
        """
        self.period = period
        self.time_delay = time_delay
        
    def saturation_rate(self, t: float) -> float:
        """
        Returns the saturation rate at a given time.
        
        t : float
            The current time [s]. 
        """
        if np.sin(2*np.pi*(t-self.time_delay)/self.period) > 0:
            return 1
        else:
            return 0
        
    def plot_green_light(self, plt, tot_time):
        k = int(tot_time/self.period)
        
        for i in range(k):
            start = i*self.period+self.time_delay
            
            plt.axvspan(start, start+self.period/2, facecolor='g', alpha=0.2)