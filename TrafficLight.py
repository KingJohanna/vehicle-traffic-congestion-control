import numpy as np
import random

class SimpleTrafficLight:
    def __init__(self):
        """
        period : float
            The period of the on/off-sequence.
        time_delay : float
            The time delay of the sequence. Light is green after after time_delay seconds has passed.
        """
        self.period = 0.
        self.time_delay = 0.
        self.time = 0.
        
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
    
    def time_step(self, delta_t: float) -> None:
        """
        Elapses time by one time-step
        """
        self.time += delta_t
        
    def saturation_rate(self, delta_t=0.) -> float:
        """
        Returns the saturation rate for a given time.
        
        t : float
            The current time [s].
        """
        if np.sin(2*np.pi*(self.time-self.time_delay)/self.period) > 0:
            return 1
        else:
            return 0
        
    def plot_green_light(self, plt, end_time):
        """
        Plots the intervals when there was green light.
        
        plt : matplotlib.pyplot
            The pyplot instance on which the plot will appear.
        end_time : float
            The end time of the plot.
        """
        k = int(end_time/self.period)
        
        for i in range(k):
            start = i*self.period+self.time_delay
            
            plt.axvspan(start, start+self.period/2, facecolor='g', alpha=0.2)
            
class MemoryLessTrafficLight:
    def __init__(self):
        """
        service : bool
            Determines whether the traffic light is at service or not.
        green_to_red_rate : float
            Probability of a green to red transition.
        red_to_green_rate : float
            Probability of a red to green transition.
        time : float
            The current simulation time.
        """
        self.service = bool(random.getrandbits(1))
        self.green_to_red_probability = 0.
        self.red_to_green_probability = 0.
        
    def initialize(self, green_to_red_rate: float, red_to_green_rate: float) -> None:
        """
        Initializes the SimpleTrafficLight instance.
        
        green_to_red_rate : float
            Probability of a green to red transition.
        red_to_green_rate : float
            Probability of a red to green transition.
        """
        self.green_to_red_rate = green_to_red_rate
        self.red_to_green_rate = red_to_green_rate
        
    def time_step(self, delta_t: float) -> None:
        """
        Elapses time by one time-step.
        
        delta_t : float
            Time-step size
        """
        if self.service and random.random() < delta_t*self.green_to_red_rate:
            self.service = False
        elif not self.service and random.random() < delta_t*self.red_to_green_rate:
            self.service = True
            
        self.time += delta_t
            
    def saturation_rate(self, delta_t=0.) -> float:
        """
        Returns the current saturation rate.
        """
        
        return self.service
    
class MemoryLessTrafficLightMirror:
    def __init__(self):
        """
        traffic_light : MemoryLessTrafficLight
            The traffic light instance to mirror.
        time : float
            The current simulation time [s].
        """
        self.traffic_light = None
        self.time = 0.
        
    def initialize(self, traffic_light: MemoryLessTrafficLight) -> None:
        """
        Initializes the MemoryLessTrafficLightMirror instance.
        
        traffic_light : MemoryLessTrafficLight
            The traffic light instance to mirror.
        """
        self.traffic_light = traffic_light
        
    def time_step(self, delta_t: float) -> None:
        """
        Elapses time by one time-step.
        
        delta_t : float
            The time-step size.
        """
        self.time += delta_t
        
    def saturation_rate(self, delta_t=0.):
        """
        Returns the current saturation rate.
        """
        return float(not self.traffic_light.service)