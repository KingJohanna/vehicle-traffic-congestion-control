import BaseModel
from scipy.stats import poisson
from scipy.stats import expon
import random
import numpy as np
import Vehicle
import TrafficLight
import math
    
class PoissonQueueSimulator(BaseModel.QueueSimulator):    
    def time_until_arrival(self) -> float:
        """
        Returns a sampled time until next arrival [s]. 
        """
        rate = self.queue.arrival_rate(self.time)
        if rate > 0:
            return np.random.exponential(scale=1/rate)
        else:
            return np.inf
    
    def time_to_depart(self) -> float:
        """
        Returns a sampled time to depart [s].
        """
        return np.random.exponential(scale=1/self.queue.departure_rate)
    
    def arrival_probability(self) -> float:
        rate = self.queue.arrival_rate(self.time)
        
        if rate > 0:
            return expon.cdf(self.time_since_arrival, scale=1/rate)
        
        return 0
    
    def run_event(self, delta_t: float, saturation_rate: float, animate=False, plt=None) -> Vehicle.Vehicle:
        """
        Runs all events (arrivals/departures) given the current circumstances and elapses time.
        
        delta_t : float
            The time-step size [s].
        saturation_rate : float
            The current saturation rate. Determined by an external traffic light.
        """
        self.update_vehicle_positions(delta_t=delta_t, saturation_rate=saturation_rate)
        
        arriving_vehicles = []
        departing_vehicle = None
        
        if self.random_variable < self.arrival_probability():
            platoon_size = np.random.choice(range(1,len(self.queue.platoon_size_distribution)+1), p=self.queue.platoon_size_distribution)
            
            for i in range(platoon_size):
                arriving_vehicles += [self.generate_vehicle()]
                
                if platoon_size > 1:
                    vehicle = arriving_vehicles[-1]
            
            self.arrivals += [self.arrivals[-1]+platoon_size]
            self.random_variable = random.random()
        else:
            self.arrivals += [self.arrivals[-1]]
        
        self.update_vehicle_positions(delta_t=delta_t, saturation_rate=saturation_rate)
        
        if saturation_rate <= 0:
            self.time_served = 0
        
        if saturation_rate > 0:
            departing_vehicle = self.queue.remove()
            if departing_vehicle != None:
                self.time_served = 0
                self.departures += [self.departures[-1]+1]
                self.tot_wait_time += departing_vehicle.wait_time
                departing_vehicle.wait_time = 0
                departing_vehicle.accelerate()
                self.next_time_to_depart = self.time_to_depart()
            else:
                self.departures += [self.departures[-1]]
                self.time_served = 0
        else:
            self.departures += [self.departures[-1]]
        
        self.queue_length += [self.queue.queue_length]
        self.time_step(delta_t=delta_t)
        
        return arriving_vehicles, departing_vehicle
    
class ConnectedQueueSimulator(BaseModel.QueueSimulator):
    def time_to_depart(self) -> float:
        """
        Returns a sampled time to depart [s].
        """
        return np.random.exponential(scale=1/self.queue.departure_rate)

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
        else:
            self.arrivals += [self.arrivals[-1]+1]
        
        if saturation_rate <= 0:
            self.time_served = 0

        self.update_vehicle_positions(delta_t=delta_t, saturation_rate=saturation_rate)
        
        if saturation_rate > 0:
            departing_vehicle = self.queue.remove()
            if departing_vehicle != None:
                self.time_served = 0
                self.departures += [self.departures[-1]+1]
                self.tot_wait_time += departing_vehicle.wait_time
                departing_vehicle.wait_time = 0
                departing_vehicle.accelerate()
                self.next_departure_time = self.time_to_depart()
            else:
                self.departures += [self.departures[-1]]
                self.time_served = 0
        else:
            self.departures += [self.departures[-1]]
        
        self.queue_length += [self.queue.queue_length]
        self.time_step(delta_t=delta_t)
        
        return [], departing_vehicle
    
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
        self.estimator = None
        self.horizontal_crossers = []
        self.vertical_crossers = []
        self.num_queued_vehicles = [0]
        self.avg_clearance_rate_ns = 0.
        self.avg_clearance_rate_ew = 0.
        self.arrivals = 0
        self.arrivals_on_green = 0
        self.arrivals_on_green_rate = 0.
        self.cum_clearance_rate_ns = 0.
        self.cum_clearance_rate_ew = 0.
        self.avg_wait_time = 0.
        
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
        self.edge_type = PoissonQueueSimulator
        self.intersection_type = FourWayIntersectionSimulator
        self.intersections = None
        self.grid_inds = []
        self.vehicles = set()
        self.time = 0.
        self.tot_wait_time = 0.
        self.exits = [0]
        self.observations = []
        self.avg_wait_time = 0.
        self.observable_intersection_grid_inds = []
        self.homogeneous = True