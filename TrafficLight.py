import numpy as np
import random

class TrafficLight:
    def __init__(self):
        self.visuals = [None, None]
        self.service = False
        self.service_history = [self.service]
        self.positions = [(0,0), (0,0)]
        self.time = 0
        self.adaptive = False
        
    def time_step(self, delta_t: float) -> None:
        """
        Elapses time by one time-step
        """
        self.time += delta_t
        self.service = self.saturation_rate()
        self.service_history += [self.service]
        
    def initialize_plot(self, plt) -> None:
        for i,pos in enumerate(self.positions):
            self.visuals[i], = plt.plot(pos[0], pos[1], 'o', markersize = 6)

    def update_plot(self) -> None:
        if bool(self.service):
            for vis in self.visuals:
                vis.set_color('green')
        else:
            for vis in self.visuals:
                vis.set_color('red')
                
    def plot_green_light(self, ax, time):
        y_lim = ax.get_ylim()
        
        ax.fill_between(time, y_lim[0], y_lim[1], where=self.service_history[:len(time)], facecolor='g', alpha=0.2)
        
    def reset(self):
        self.service = self.saturation_rate()
        self.service_history = [self.service]
        self.time = 0.
        
        return self
        
class TrafficLightMirror(TrafficLight):
    def __init__(self):
        """
        traffic_light : TrafficLight
            The traffic light instance to mirror.
        time : float
            The current simulation time [s].
        """
        self.traffic_light = None
        self.time = 0.
        self.visuals = [None, None]
        self.positions = [(0,0), (0,0)]
        self.service = False
        self.service_history = []
        self.adaptive = False
        
    def initialize(self, traffic_light: TrafficLight) -> None:
        """
        Initializes the MemoryLessTrafficLightMirror instance.
        
        traffic_light : MemoryLessTrafficLight
            The traffic light instance to mirror.
        """
        self.traffic_light = traffic_light
        self.service = not traffic_light.service
        self.service_history += [self.service]
        
    def saturation_rate(self, delta_t=0.):
        """
        Returns the current saturation rate.
        """
        self.service = float(not self.traffic_light.service)
        
        return float(not self.traffic_light.service)

class PeriodicTrafficLight(TrafficLight):
    def __init__(self):
        """
        period : float
            The period of the on/off-sequence.
        time_delay : float
            The time delay of the sequence. Light is green after after time_delay seconds has passed.
        """
        self.period = 0.
        self.time_delay = 0.
        self.green_ratio = 0.
        self.time = 0.
        self.visuals = [None, None]
        self.positions = [(0,0), (0,0)]
        self.service = False
        self.service_history = [self.service]
        self.adaptive = False
        
    def initialize(self, period: float, time_delay: float, green_ratio=0.5) -> None:
        """
        Initializes the SimpleTrafficLight instance.
        
        period : float
            The period of the on/off-sequence.
        time_delay : float
            The time delay of the sequence.
        """
        self.period = period
        self.time_delay = time_delay
        self.green_ratio = green_ratio
        
    def saturation_rate(self, delta_t=0.) -> float:
        """
        Returns the saturation rate for a given time.
        
        t : float
            The current time [s].
        """
        if ((self.time-self.time_delay) % self.period)/self.period < self.green_ratio:
            return 1
        else:
            return 0
            
class MemoryLessTrafficLight(TrafficLight):
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
        self.service_history = [self.service]
        self.green_to_red_probability = 0.
        self.red_to_green_probability = 0.
        self.time = 0.
        self.visuals = [None, None]
        self.positions = [(0,0), (0,0)]
        self.adaptive = False
        
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
            
        self.service_history += [self.service]
        self.time += delta_t
            
    def saturation_rate(self, delta_t=0.) -> float:
        """
        Returns the current saturation rate.
        """
        
        return self.service
    
class AdaptiveTrafficLight(TrafficLight):
    global EMPTY, EMPTY_OTHER, EMPTY_HALFWAY, EMPTY_OTHER_HALFWAY, WAIT
    
    EMPTY = 0
    EMPTY_OTHER = 1
    EMPTY_HALFWAY = 2
    EMPTY_OTHER_HALFWAY = 3
    WAIT = 4
    
    def __init__(self):
        self.visuals = [None, None]
        self.service = False
        self.service_history = [self.service]
        self.positions = [(0,0), (0,0)]
        self.time = 0
        self.adaptive = True
        self.initial_length = 0
        self.case = WAIT
    
    def sense(self, queue_length: int, opposite_queue_length: int) -> None:
        if self.case == WAIT: # Queue has been emptied, check if traffic light should switch
            if opposite_queue_length > 0:
                self.case = EMPTY_OTHER
            elif queue_length > 0:
                self.case = EMPTY
                
        if self.case in [EMPTY, EMPTY_OTHER]: # Check if the other queue has become too long while emptying current queue
            if queue_length >= 2*(opposite_queue_length+2):
                self.case = EMPTY_HALFWAY
                self.initial_length = queue_length
            elif opposite_queue_length >= 2*(queue_length+2):
                self.case = EMPTY_OTHER_HALFWAY
                self.initial_length = opposite_queue_length
        
        if self.case == EMPTY: # Check if current objective has been completed
            if queue_length <= 0:
                self.case = WAIT
            else:
                self.service = True
        elif self.case == EMPTY_HALFWAY:
            if queue_length <= self.initial_length/2:
                self.case = EMPTY_OTHER
            else:
                self.service = True
        elif self.case == EMPTY_OTHER:
            if opposite_queue_length <= 0:
                self.case = WAIT
            else:
                self.service = False
        elif self.case == EMPTY_OTHER_HALFWAY:
            if opposite_queue_length <= self.initial_length/2:
                self.case = EMPTY
            else:
                self.service = False
            
    
    def saturation_rate(self, delta_t=0.):
        return self.service