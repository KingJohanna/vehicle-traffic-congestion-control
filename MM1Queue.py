from scipy.stats import poisson
from scipy.stats import expon
import random

class Queue:
    def __init__(self):
        self.queue_length = 0
        self.departures = 0
        self.arrivals = 0
        self.arrival_rate = 0 # vehicles per second
        self.departure_rate = 0 # vehicles per second
    
    def initialize(self, avg_arrival_time: float, avg_departure_time: float) -> None:
        self.arrival_rate = 1/avg_arrival_time
        self.departure_rate = 1/avg_departure_time
    
    def append(self) -> None:
        self.queue_length += 1
        self.arrivals += 1
        
    def remove(self) -> None:
        if self.queue_length > 0:
            self.queue_length -= 1
            self.departures += 1
            
class QueueSimulator:
    def __init__(self):
        self.queue = Queue()
        self.time = 0
        self.time_since_arrival = 0
        self.time_served = 0
        
    def initialize(self, avg_arrival_time: float, avg_departure_time: float) -> None:
        self.queue.initialize(avg_arrival_time=avg_arrival_time, avg_departure_time=avg_arrival_time)
        
    def time_step(self, delta_t: float) -> None:
        self.time += delta_t
        self.time_since_arrival += delta_t
        self.time_served += delta_t
        
    def arrival_probability(self) -> float:
        return poissin.cdf(x=self.time_since_arrival, mu=self.queue.arrival_rate)
        
    def departure_probability(self, saturation_rate: float) -> float:
        if saturation_rate == 0:
            self.time_served = 0 # departure process is not active at red light
            return 0
        
        return saturation_rate*expon.cdf(x=self.time_served, scale=1/self.queue.departure_rate)

    def run_event(self, delta_t: float) -> None: # Check for vehicle arrivals/departures at current time, then execute time-step
        if random.random() < self.arrival_probability():
            self.queue.remove()
            self.time_since_arrival = 0
        
        if random.random() < self.departure_probability():
            self.queue.remove()
            self.time_served = 0
            
        self.time_step()
        