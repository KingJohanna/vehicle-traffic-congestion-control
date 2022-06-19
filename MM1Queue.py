from scipy.stats import poisson
from scipy.stats import expon
import random

class Queue:
    def __init__(self):
        """
        queue_length : int
            Nbr of vehicles in the queue.
        arrival_rate : float
            Rate at which vehicles arrive to the queue [1/s].
        departure_rate : float
            Rate at which vehicles depart from the queue [1/s].
        """
        self.queue_length = 0
        self.arrival_rate = 0
        self.departure_rate = 0
    
    def initialize(self, avg_arrival_time: float, avg_departure_time: float) -> None:
        """
        Initializes the Queue instance.
        
        avg_arrival_time : float
            The average time between arrivals to the queue.
        avg_departure_time : float
            The average time between departures from the queue.
        random_arrivals : bool
            Determines whether the arrival process is stochastic or not.
        """
        self.arrival_rate = 1/avg_arrival_time
        self.departure_rate = 1/avg_departure_time
    
    def append(self) -> None:
        """
        Appends a vehicle to the queue.
        """
        self.queue_length += 1
        
    def remove(self) -> None:
        """
        Removes a vehicle from the queue.
        """
        if self.queue_length > 0:
            self.queue_length -= 1
            
class ConnectedQueue:
    def __init__(self):
        """
        queue_length : int
            Nbr of vehicles in the queue.
        departure_rate : float
            Rate at which vehicles depart from the queue [1/s].
        """
        self.queue_length = 0
        self.departure_rate = 0
    
    def initialize(self, avg_departure_time: float) -> None:
        """
        Initializes the ConnectedQueue instance.
        
        avg_departure_time : float
            The average time between departures from the queue.
        """
        self.departure_rate = 1/avg_departure_time
    
    def append(self) -> None:
        """
        Appends a vehicle to the queue.
        """
        self.queue_length += 1
        
    def remove(self) -> None:
        """
        Removes a vehicle from the queue.
        """
        if self.queue_length > 0:
            self.queue_length -= 1
            
class MM1QueueSimulator:
    def __init__(self):
        """
        queue : Queue
            The internal Queue instance.
        time : float
            The current simulation time [s].
        time_since_arrival : float
            Time since last arrival to the queue [s].
        time_served : float
            Amount of time frontmost vehicle has been served without departing from queue [s].
        queue_length : list(int)
            Nbr of vehicles in queue over time.
        departures : list(int)
            Total nbr of departures over time.
        arrivals : list(int)
            Totalt nbr of arrivals over time.
        tot_wait_time : float
            Total wait time for all vehicles that are and have been in the queue.
        next_queue : QueueSimulator
            Another queue connected to this queue.
        next_queue_distance : float
            Distance [s] to the connected queue.
        next_queue_timestamps : list(float)
            Timestamps of each vehicle arriving to next_queue.
        """
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

    def initialize(self, avg_departure_time: float, avg_arrival_time=0.) -> None:
        """
        Initializes the QueueSimulator instance.
        
        avg_arrival_time (optional) : float
            The average time between arrivals to the queue. Defaults to 0.
        avg_departure_time : float
            The average time between departures from the queue.
        random_arrivals (optional): bool
            Determines whether the arrival process is stochastic or not. Defaults to True.
        """
        self.queue.initialize(avg_arrival_time=avg_arrival_time, avg_departure_time=avg_departure_time)
        
    def connect_queue(self, next_queue, distance: 0.) -> None:
        """
        Connects the queue to a ConnectedQueueSimulator instance. Departures from this queue are set to arrive to next_queue.
        
        next_queue : ConnectedQueueSimulator
            The queue in front of this queue.
        distance (optional) : float
            The distance [s] to the other queue.
        """
        self.next_queue = next_queue
        self.next_queue_distance = distance
        
    def time_step(self, delta_t: float) -> None:
        """
        Elapses time by one time-step.
        
        delta_t : float
            The time-step size.
        """
        self.time += delta_t
        self.time_since_arrival += delta_t
        self.time_served += delta_t
        self.tot_wait_time += delta_t*self.queue.queue_length
        
    def arrival_probability(self) -> float:
        """
        Returns the probability of an arrival occuring at current time.
        """
        if self.time_since_arrival > 0:
            return 1-poisson.cdf(k=1/self.time_since_arrival, mu=self.queue.arrival_rate)
        return 0
        
    def departure_probability(self, saturation_rate: float) -> float:
        """
        Returns the probability of a departure occuring at current time.
        
        saturation_rate : float
            The current saturation rate. Determined by an external traffic light.
        """
        if saturation_rate == 0:
            self.time_served = 0 # departure process is not active at red light
            return 0
        
        return saturation_rate*expon.cdf(x=self.time_served, scale=1/self.queue.departure_rate)

    def run_event(self, delta_t: float, saturation_rate: float) -> None:
        """
        Runs all events (arrivals/departures) given the current circumstances and elapses time.
        """
        if len(self.next_queue_timestamps) > 0: # Check if prev. departed vehicles have reached next queue
            if self.next_queue_timestamps[0] < self.time:
                self.next_queue.arrival = True
                self.next_queue_timestamps = self.next_queue_timestamps[1:]
        
        if random.random() < self.arrival_probability():
            self.queue.append()
            self.time_since_arrival = 0
            self.arrivals += [self.arrivals[-1]+1]
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
        
    def avg_wait_time(self) -> float:
        """
        Returns the average waiting time in the queue.
        """
        return self.tot_wait_time/len(self.departures)
    
    def get_stats(self) -> (list, list, list, float):
        """
        Returns stats.
        """
        return self.queue_length, self.departures, self.arrivals, self.avg_wait_time()
    
class ConnectedQueueSimulator:
    def __init__(self):
        """
        queue : Queue
            The internal Queue instance.
        time : float
            The current simulation time [s].
        time_since_arrival : float
            Time since last arrival to the queue [s].
        time_served : float
            Amount of time frontmost vehicle has been served without departing from queue [s].
        queue_length : list(int)
            Nbr of vehicles in queue over time.
        departures : list(int)
            Total nbr of departures over time.
        arrivals : list(int)
            Totalt nbr of arrivals over time.
        tot_wait_time : float
            Total wait time for all vehicles that are and have been in the queue.
        next_queue : QueueSimulator
            Another queue connected to this queue.
        next_queue_distance : float
            Distance [s] to the connected queue.
        next_queue_timestamps : list(float)
            Timestamps of each vehicle arriving to next_queue.
        arrival : bool
            Determines whether a vehicle has arrived at the current time.
        """
        self.queue = ConnectedQueue()
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
        """
        Initializes the QueueSimulator instance.
        
        avg_arrival_time (optional) : float
            The average time between arrivals to the queue. Defaults to 0.
        avg_departure_time : float
            The average time between departures from the queue.
        random_arrivals (optional): bool
            Determines whether the arrival process is stochastic or not. Defaults to True.
        """
        self.queue.initialize(avg_departure_time=avg_departure_time)
        
    def time_step(self, delta_t: float) -> None:
        """
        Elapses time by one time-step.
        
        delta_t : float
            The time-step size.
        """
        self.time += delta_t
        self.time_since_arrival += delta_t
        self.time_served += delta_t
        self.tot_wait_time += delta_t*self.queue.queue_length
        
    def departure_probability(self, saturation_rate: float) -> float:
        """
        Returns the probability of a departure occuring at current time.
        
        saturation_rate : float
            The current saturation rate. Determined by an external traffic light.
        """
        if saturation_rate == 0:
            self.time_served = 0 # departure process is not active at red light
            return 0
        
        return saturation_rate*expon.cdf(x=self.time_served, scale=1/self.queue.departure_rate)

    def run_event(self, delta_t: float, saturation_rate: float) -> None:
        """
        Runs all events (arrivals/departures) given the current circumstances and elapses time.
        """      
        if self.arrival:
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
        
    def avg_wait_time(self) -> float:
        """
        Returns the average waiting time in the queue.
        """
        return self.tot_wait_time/len(self.departures)
    
    def get_stats(self) -> (list, list, list, float):
        """
        Returns stats.
        """
        return self.queue_length, self.departures, self.arrivals, self.avg_wait_time()