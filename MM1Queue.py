from scipy.stats import poisson
from scipy.stats import expon
import random
import queue

class Queue:
    def __init__(self):
        # self.vehicles = queue.Queue()
        self.queue_length = 0
        self.arrival_rate = 0 # vehicles per second
        self.departure_rate = 0 # vehicles per second
    
    def initialize(self, avg_arrival_time: float, avg_departure_time: float, random_arrivals: bool) -> None:
        if random_arrivals:
            self.arrival_rate = 1/avg_arrival_time
        self.departure_rate = 1/avg_departure_time
        self.random_arrivals = random_arrivals
    
    def append(self) -> None:
        self.queue_length += 1
        
    def remove(self) -> None:
        if self.queue_length > 0:
            self.queue_length -= 1
            
class QueueSimulator:
    def __init__(self):
        self.queue = Queue()
        self.time = 0
        self.time_since_arrival = 0
        self.time_served = 0
        self.queue_length = [0]
        self.departures = [0]
        self.arrivals = [0]
        self.tot_wait_time = 0
        
        self.next_queue = None
        self.next_queue_distance = 0. # [s]
        self.next_queue_timestamps = [] # Timestamps of when vehicles are to arrive to next queue
        
        self.arrival = False
        
    def initialize(self, avg_departure_time: float, random_arrivals=True, avg_arrival_time=0.) -> None:
        self.queue.initialize(avg_arrival_time=avg_arrival_time, avg_departure_time=avg_departure_time, random_arrivals=random_arrivals)
        
    def connect_queue(self, queue, distance: 0.) -> None: # Connect this queue to another one in front
        self.next_queue = queue
        self.next_queue_distance = distance
        
    def time_step(self, delta_t: float) -> None:
        self.time += delta_t
        self.time_since_arrival += delta_t
        self.time_served += delta_t
        self.tot_wait_time += delta_t*self.queue.queue_length
        
    def arrival_probability(self) -> float:
        return poisson.cdf(k=self.time_since_arrival, mu=1/self.queue.arrival_rate)
        
    def departure_probability(self, saturation_rate: float) -> float:
        if saturation_rate == 0:
            self.time_served = 0 # departure process is not active at red light
            return 0
        
        return saturation_rate*expon.cdf(x=self.time_served, scale=1/self.queue.departure_rate)

    def run_event(self, delta_t: float, saturation_rate: float) -> None: # Check for vehicle arrivals/departures at current time, then execute time-step
        if len(self.next_queue_timestamps) > 0: # Check if prev. departed vehicles have reached next queue
            if self.next_queue_timestamps[0] < self.time:
                self.next_queue.arrival = True
                self.next_queue_timestamps = self.next_queue_timestamps[1:]
        
        if self.queue.random_arrivals:
            if random.random() < self.arrival_probability():
                self.queue.append()
                self.time_since_arrival = 0
                self.arrivals += [self.arrivals[-1]+1]
        elif self.arrival:
            self.queue.append()
            self.time_since_arrival = 0
            self.arrivals += [self.arrivals[-1]+1]
            self.arrival = False
        else:
            self.arrivals += [self.arrivals[-1]]

        if random.random() < self.departure_probability(saturation_rate=saturation_rate):
            self.queue.remove()
            self.time_served = 0
            self.departures += [self.departures[-1]+1]
            if self.next_queue != None:
                self.next_queue_timestamps += [self.time+self.next_queue_distance]
        else:
            self.departures += [self.departures[-1]]
        
        self.queue_length += [self.queue.queue_length]
        self.time_step(delta_t=delta_t)
        
    def avg_wait_time(self) -> float: # Some inaccuracy since tot_wait_time includes wait times of undeparted vehicles
        return self.tot_wait_time/len(self.departures)
    
    def get_stats(self) -> (list, list, list, float):
        return self.queue_length, self.departures, self.arrivals, self.avg_wait_time()
        