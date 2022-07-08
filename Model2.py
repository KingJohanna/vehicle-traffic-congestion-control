import BaseModel
import random
import numpy as np
import Vehicle
import TrafficLight
import math

class SingleQueueSimulator(BaseModel.QueueSimulator):
    def arrival_probability(self, delta_t: float) -> float:
        """
        Returns the probability of an arrival occurring within a time-step.
        
        delta_t : float
            Time-step size.
        """
        return delta_t*self.queue.arrival_rate
        
    def departure_probability(self, delta_t: float, saturation_rate) -> float:
        """
        Returns the probability of a departure occurring within a time-step.
        
        delta_t : float
            Time-step size.
        """
        if saturation_rate == 0:
            return 0
        
        return delta_t*self.queue.departure_rate
    
    def run_event(self, delta_t: float, saturation_rate: float, animate=False, plt=None) -> Vehicle.Vehicle:
        """
        Runs all events (arrivals/departures) given the current circumstances and elapses time.
        
        delta_t : float
            The time-step size [s].
        saturation_rate : float
            The current saturation rate. Determined by an external traffic light.
        """
        arriving_vehicle = None
        departing_vehicle = None
        
        if random.random() < self.arrival_probability(delta_t=delta_t):
            arriving_vehicle = Vehicle.Vehicle()
            arriving_vehicle.initialize(position=self.queue.tail_position, direction=self.queue.direction)
            if animate:
                arriving_vehicle.initialize_plot(plt=plt)
            self.queue.append(arriving_vehicle)
            self.time_since_arrival = 0
            self.arrivals += [self.arrivals[-1]+1]
        else:
            self.arrivals += [self.arrivals[-1]]

        if random.random() < self.departure_probability(delta_t=delta_t, saturation_rate=saturation_rate):
            departing_vehicle = self.queue.remove()
            if departing_vehicle != None:
                self.time_served = 0
                self.departures += [self.departures[-1]+1]
                self.tot_wait_time += departing_vehicle.wait_time
                departing_vehicle.accelerate()
            else:
                self.departures += [self.departures[-1]]
        else:
            self.departures += [self.departures[-1]]
        
        self.queue_length += [self.queue.queue_length]
        self.time_step(delta_t=delta_t)
        
        return arriving_vehicle, departing_vehicle

class ConnectedQueueSimulator(BaseModel.ConnectedQueueSimulator):
    def departure_probability(self, delta_t: float, saturation_rate) -> float:
        """
        Returns the probability of a departure occurring within a time-step.
        
        delta_t : float
            Time-step size.
        """
        if saturation_rate == 0:
            return 0
        
        return delta_t*self.queue.departure_rate
        
    def run_event(self, delta_t: float, saturation_rate: float, animate=False, plt=None) -> None:
        """
        Runs all events (departures) given the current circumstances and elapses time.
        
        delta_t: float
            The time-step size [s].
        saturation_rate : float
            The current saturation rate. Determined by an external traffic light.
        """ 
        departing_vehicle = None
        
        if self.time_since_arrival > 0:
            self.arrivals += [self.arrivals[-1]]
        
        if random.random() < self.departure_probability(delta_t=delta_t, saturation_rate=saturation_rate):
            departing_vehicle = self.queue.remove()
            if departing_vehicle != None:
                self.time_served = 0
                self.departures += [self.departures[-1]+1]
                self.tot_wait_time += departing_vehicle.wait_time
                departing_vehicle.accelerate()
            else:
                self.departures += [self.departures[-1]]
        else:
            self.departures += [self.departures[-1]]
        
        self.queue_length += [self.queue.queue_length]
        self.time_step(delta_t=delta_t)
        
        return None, departing_vehicle
    
class FourWayIntersectionSimulator(BaseModel.FourWayIntersectionSimulator):
    def __init__(self):
        """
        queue_n : ConnectedQueueSimulator
            The northbound queue.
        queue_w : ConnectedQueueSimulator
            The westbound queue.
        queue_s : ConnectedQueueSimulator
            The southbound queue.
        queue_e : ConnectedQueueSimulator
            The eastbound queue.
        traffic_light_ns : TrafficLight.SimpleTrafficLight
            The traffic light controlling the north- and southbound queues.
        traffic_light_ew : TrafficLight.SimpleTrafficLight
            The traffic light controlling the east- and westbound queues.
        position : (float, float)
            The centerpoint of the intersection.
        length : float
            The width of the roads.
        time : float
            The current simulation time [s].
        """
        self.queue_n = ConnectedQueueSimulator()
        self.queue_w = ConnectedQueueSimulator()
        self.queue_s = ConnectedQueueSimulator()
        self.queue_e = ConnectedQueueSimulator()
        self.traffic_light_ns = None
        self.traffic_light_ew = None
        self.position = (0.,0.)
        self.length = 0.
        self.time = 0.
        self.observable = False
        
class IntersectionNetworkSimulator(BaseModel.IntersectionNetworkSimulator):
    def __init__(self):
        """
        grid_dimensions : (int,int)
            The grid dimensions of the intersection network.
        grid_distance : float
            The distance [m] between each intersection centerpoint.
        intersections : [FourWayIntersectionSimulator]
            The intersections contained in the network.
        grid_inds : [(int,int)]
            The grid indices within the network.
        moving_vehicles : [Vehicle.Vehicle]
            The vehicles within the network, not contained in any queue.
        time : float
            The current simulation time [s].
        """
        self.grid_dimensions = (0,0)
        self.grid_distance = 0.
        self.edge_type = SingleQueueSimulator
        self.intersection_type = FourWayIntersectionSimulator
        self.intersections = None
        self.grid_inds = []
        self.vehicles = set()
        self.time = 0.
        self.observations = []