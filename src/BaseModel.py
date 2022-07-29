import random
import numpy as np
import Vehicle
import TrafficLight
import math
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as manimation
import pickle as pkl
from pathlib import Path

class Queue:
    def __init__(self):
        """
        vehicles : list(Vehicle.Vehicle)
            List (FIFO) of vehicles contained within this queue.
        direction : (float, float)
            Travel direction of this queue.
        head_position : (float, float)
            Position of the queue's head.
        tail_position : (float, float)
            Position of the queue's tail.
        queue_length : int
            Nbr of vehicles in the queue.
        arrival_rate : float
            Rate at which vehicles arrive to the queue [1/s].
        departure_rate : float
            Rate at which vehicles depart from the queue [1/s].
        """
        self.vehicles = []
        self.departing_vehicle = None
        self.last_arriving_vehicle = None
        self.direction = (0, 0)
        self.head_position = (0, 0)
        self.tail_position = (0, 0)
        self.edge_position = (0, 0)
        self.queue_length = 0
        self.arrival_rate = 0
        self.departure_rate = 0
    
    def initialize(self, avg_departure_time: float, direction: (int, int), head_position: (float, float), arrival_rate=lambda t: 0) -> None:
        """
        Initializes the Queue instance.
        
        arrival_rate : float (optional)
            The average time [s] between arrivals to the queue. Defaults to infinity.
        avg_departure_time : float
            The average time [s] between departures from the queue.
        direction: (float, float)
            Travel direction of this queue.
        head_position : (float, float)
            Position of the queue's head.
        """
        self.arrival_rate = arrival_rate
        self.departure_rate = 1/avg_departure_time
        self.direction = direction
        self.head_position = head_position
        self.tail_position = head_position
        self.edge_position = (head_position[0]-direction[0]*50, head_position[1]-direction[1]*50)
    
    def append(self, vehicle: Vehicle.Vehicle) -> bool:
        """
        Appends a vehicle to the queue.
        
        vehicle : Vehicle.Vehicle
            The vehicle to be appended to the queue.
        """
        if vehicle not in self.vehicles:
            #vehicle.stop()
            if len(self.vehicles) > 0:
                if vehicle.speed <= 0:
                    vehicle.update_position(new_position=(self.tail_position[0]-2*self.direction[0], self.tail_position[1]-2*self.direction[1]))
            else:
                if vehicle.speed <= 0:
                    vehicle.update_position(new_position=(self.tail_position[0], self.tail_position[1]))
            self.vehicles += [vehicle]
            self.queue_length = len(self.vehicles)
             
            return True
        return False
        
    def remove(self) -> Vehicle.Vehicle:
        """
        Removes a vehicle from the queue.
        """
        if len(self.vehicles) > 0:
            departing_vehicle = self.vehicles[0]
            
            if (departing_vehicle.direction == Vehicle.NORTH and departing_vehicle.position[1] >= self.head_position[1]) or (departing_vehicle.direction == Vehicle.EAST and departing_vehicle.position[0] >= self.head_position[0]) or (departing_vehicle.direction == Vehicle.SOUTH and departing_vehicle.position[1] <= self.head_position[1]) or (departing_vehicle.direction == Vehicle.WEST and departing_vehicle.position[0] <= self.head_position[0]):
                self.vehicles.remove(departing_vehicle)
                self.queue_length = len(self.vehicles)
                self.update_tail_position()
                self.departing_vehicle = departing_vehicle
                
                if departing_vehicle == self.last_arriving_vehicle:
                    self.last_arriving_vehicle = None
                
                return departing_vehicle
                
        return None
    
    def update_tail_position(self) -> None:
        if len(self.vehicles) > 0:
            self.tail_position = self.vehicles[-1].tail_position
            
        elif self.departing_vehicle != None:
            if self.departing_vehicle.direction == Vehicle.NORTH:
                if self.departing_vehicle.tail_position[1] > self.head_position[1]:
                    self.departing_vehicle = None
                    self.tail_position = self.head_position
                else:
                    self.tail_position = (self.departing_vehicle.tail_position[0], self.departing_vehicle.tail_position[1]-2)
                        
            elif self.departing_vehicle.direction == Vehicle.EAST:
                if self.departing_vehicle.tail_position[0] > self.head_position[0]:
                    self.departing_vehicle = None
                    self.tail_position = self.head_position
                else:
                    self.tail_position = (self.departing_vehicle.tail_position[0]-2, self.departing_vehicle.tail_position[1])
                    
            elif self.departing_vehicle.direction == Vehicle.SOUTH:
                if self.departing_vehicle.tail_position[1] < self.head_position[1]:
                    self.departing_vehicle = None
                    self.tail_position = self.head_position
                else:
                    self.tail_position = (self.departing_vehicle.tail_position[0], self.departing_vehicle.tail_position[1]+2)
                    
            elif self.departing_vehicle.direction == Vehicle.WEST:
                if self.departing_vehicle.tail_position[0] < self.head_position[0]:
                    self.departing_vehicle = None
                    self.tail_position = self.head_position
                else:
                    self.tail_position = (self.departing_vehicle.tail_position[0]+2, self.departing_vehicle.tail_position[1])
                    
        else:
            self.tail_position = self.head_position
        
class ConnectedQueue(Queue):
    def __init__(self):
        """
        vehicles : list(Vehicle.Vehicle)
            List (FIFO) of vehicles contained within this queue.
        direction : (float, float)
            Travel direction of this queue.
        head_position : (float, float)
            Position of the queue's head.
        tail_position : (float, float)
            Position of the queue's tail.
        queue_length : int
            Nbr of vehicles in the queue.
        arrival_rate : float
            Rate at which vehicles arrive to the queue [1/s].
        departure_rate : float
            Rate at which vehicles depart from the queue [1/s].
        """
        self.vehicles = []
        self.direction = (0, 0)
        self.head_position = (0, 0)
        self.tail_position = (0, 0)
        self.queue_length = 0
        self.departure_rate = 0
    
    def initialize(self, avg_departure_time: float, direction: (int, int), head_position: (float, float)) -> None:
        """
        Initializes the Queue instance.
        
        arrival_rate : float (optional)
            The average time [s] between arrivals to the queue. Defaults to infinity.
        avg_departure_time : float
            The average time [s] between departures from the queue.
        direction: (float, float)
            Travel direction of this queue.
        head_position : (float, float)
            Position of the queue's head.
        """
        self.departure_rate = 1/avg_departure_time
        self.direction = direction
        self.head_position = head_position
        self.tail_position = head_position
    
class QueueSimulator:
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
        next_arrival_timestamp : float
            The timestamp at which the next arrival occurs.
        next_time_to_depart : float
            The time between the last departure and the next [s].
        """
        self.queue = Queue()
        self.time = 0
        self.time_since_arrival = 0
        self.time_served = 0
        self.queue_length = [0]
        self.departures = [0]
        self.arrivals = [0]
        self.tot_wait_time = 0
        self.next_arrival_timestamp = 0
        self.visual = None
        self.edge = True
        self.random_variable = random.random()
        
    def initialize(self, avg_departure_time=np.inf, arrival_rate=lambda t: 0, direction=Vehicle.NORTH, head_position=(0.,0.)) -> None:
        """
        Initializes the QueueSimulator instance.
        
        arrival_rate (optional) : float
            The average time [s] between arrivals to the queue. Defaults to infinity.
        avg_departure_time (optional): float
            The average time [s] between departures from the queue. Defaults to infinity.
        direction : (float, float) (optional)
            Travel direction of this queue. Defaults to Vehicle.NORTH.
        head_position : (float, float) (optional)
            Position of the queue's head. Defaults to (0.,0.).
        """
        self.queue.initialize(arrival_rate=arrival_rate, avg_departure_time=avg_departure_time, direction=direction, head_position=head_position)
        
    def initialize_plot(self, position, plt) -> None:
        if self.queue.direction == Vehicle.NORTH:
            self.visual = plt.text(position[0], position[1], "0", ha="right", va="bottom")
        elif self.queue.direction == Vehicle.WEST:
            self.visual = plt.text(position[0], position[1], "0", ha="right", va="top")
        elif self.queue.direction == Vehicle.SOUTH:
            self.visual = plt.text(position[0], position[1], "0", ha="left", va="top")
        elif self.queue.direction == Vehicle.EAST:
            self.visual = plt.text(position[0], position[1], "0", ha="left", va="bottom")
        
        
    def update_plot(self) -> None:
        self.visual.set_text(self.queue.queue_length)
        
    def time_step(self, delta_t: float) -> None:
        """
        Elapses time by one time-step.
        
        delta_t : float
            The time-step size.
        """
        self.time += delta_t
        self.time_since_arrival += delta_t
        self.time_served += delta_t
        
    def update_vehicle_positions(self, delta_t: float, saturation_rate: float) -> None:
        self.queue.update_tail_position()
        
        vehicle_tail_positions = [(vehicle.tail_position[0], vehicle.tail_position[1]) for vehicle in self.queue.vehicles]
        
        for i,vehicle in enumerate(self.queue.vehicles):
            if vehicle.direction == Vehicle.NORTH:
                if i == 0:
                    if vehicle.position[1] >= self.queue.head_position[1]:
                        if saturation_rate <= 0:
                            vehicle.stop()
                            vehicle.update_position(new_position=self.queue.head_position)
                    elif vehicle.speed <= 0 and vehicle.position != self.queue.head_position:
                        vehicle.accelerate()
                elif i > 0:
                    if vehicle.position[1] > vehicle_tail_positions[i-1][1] - vehicle.full_speed*delta_t - 2:
                        #vehicle.update_position(new_position=(vehicle_tail_positions[i-1][0], vehicle_tail_positions[i-1][1]-2))
                        if saturation_rate <= 0:
                            vehicle.stop()
                    else:
                        vehicle.accelerate()
                    
            elif vehicle.direction == Vehicle.EAST:
                if i == 0:
                    if vehicle.position[0] >= self.queue.head_position[0]:
                        if saturation_rate <= 0:
                            vehicle.stop()
                            vehicle.update_position(new_position=self.queue.head_position)
                    elif vehicle.speed <= 0 and vehicle.position != self.queue.head_position:
                        vehicle.accelerate()
                elif i > 0:
                    if vehicle.position[0] > vehicle_tail_positions[i-1][0] - vehicle.full_speed*delta_t - 2:
                        #vehicle.update_position(new_position=(vehicle_tail_positions[i-1][0]-2, vehicle_tail_positions[i-1][1]))
                        if saturation_rate <= 0:
                            vehicle.stop()
                    else:
                        vehicle.accelerate()
                    
            elif vehicle.direction == Vehicle.SOUTH:
                if i == 0:
                    if vehicle.position[1] <= self.queue.head_position[1]:
                        if saturation_rate <= 0:
                            vehicle.stop()
                            vehicle.update_position(new_position=self.queue.head_position)
                    elif vehicle.speed <= 0 and vehicle.position != self.queue.head_position:
                        vehicle.accelerate()
                elif i > 0:
                    if vehicle.position[1] < vehicle_tail_positions[i-1][1] + vehicle.full_speed*delta_t + 2:
                        #vehicle.update_position(new_position=(vehicle_tail_positions[i-1][0], vehicle_tail_positions[i-1][1]+2))
                        if saturation_rate <= 0:
                            vehicle.stop()
                    else:
                        vehicle.accelerate()
                    
            elif vehicle.direction == Vehicle.WEST:
                if i == 0:
                    if vehicle.position[0] <= self.queue.head_position[0]:
                        if saturation_rate <= 0:
                            vehicle.stop()
                            vehicle.update_position(new_position=self.queue.head_position)
                    elif vehicle.speed <= 0 and vehicle.position != self.queue.head_position:
                        vehicle.accelerate()
                elif i > 0:
                    if vehicle.position[0] < vehicle_tail_positions[i-1][0] + vehicle.full_speed*delta_t + 2:
                        #vehicle.update_position(new_position=(vehicle_tail_positions[i-1][0]+2, vehicle_tail_positions[i-1][1]))
                        if saturation_rate <= 0:
                            vehicle.stop()
                    else:
                        vehicle.accelerate()
            
    def adjust_position(self, vehicle) -> None:
        """
        Adjusts the position of the vehicle to this queue.
        """
        if self.queue.direction == Vehicle.NORTH:
            vehicle.update_position(new_position=(self.queue.head_position[0], vehicle.position[1]))
        elif self.queue.direction == Vehicle.WEST:
            vehicle.update_position(new_position=(vehicle.position[0], self.queue.head_position[1]))
        elif self.queue.direction == Vehicle.SOUTH:
            vehicle.update_position(new_position=(self.queue.head_position[0], vehicle.position[1]))
        elif self.queue.direction == Vehicle.WEST:
            vehicle.update_position(new_position=(vehicle.position[0], self.queue.head_position[1]))
        
    def avg_wait_time(self) -> float:
        """
        Returns the average waiting time in the queue.
        """
        if self.departures[-1] > 0:
            return self.tot_wait_time/self.departures[-1]
        
        return math.nan
    
    def get_stats(self) -> (list, list, list, float):
        """
        Returns stats.
        """
        return self.queue_length[1:], self.departures[1:], self.arrivals[1:], self.avg_wait_time()
    
    def generate_vehicle(self) -> None:
        vehicle = Vehicle.Vehicle()
        
        if self.queue.last_arriving_vehicle != None:
            tail_position = self.queue.last_arriving_vehicle.tail_position
        else:
            tail_position = self.queue.tail_position
            
        tail_position=(tail_position[0]-3*self.queue.direction[0], tail_position[1]-3*self.queue.direction[1])
            
        edge_distance = math.hypot(self.queue.edge_position[0]-self.queue.head_position[0], self.queue.edge_position[1]-self.head_position[1])
        tail_distance = math.hypot(tail_position[0]-self.queue.head_position[0], tail_position[1]-self.queue.head_position[1])
        
        if edge_distance > tail_distance:
            vehicle.initialize(position=self.queue.edge_position, direction=self.queue.direction)
        else:
            vehicle.initialize(position=tail_position, direction=self.queue.direction)
        
        #if (self.queue.direction == Vehicle.NORTH and tail_position[1] <= self.queue.edge_position[1]) or (self.queue.direction == Vehicle.EAST and tail_position[0] <= self.queue.edge_position[0]) or (self.queue.direction == Vehicle.SOUTH and tail_position[1] >= self.queue.edge_position[1]) or (self.queue.direction == Vehicle.WEST and tail_position[0] >= self.queue.edge_position[0]):
         #   vehicle.initialize(position=(tail_position[0]-3*self.queue.direction[0], tail_position[1]-3*self.queue.direction[1]), direction=self.queue.direction)
        #else:
         #   vehicle.initialize(position=self.queue.edge_position, direction=self.queue.direction)
           
        self.time_since_arrival = 0
        self.queue.last_arriving_vehicle = vehicle
        
        return vehicle
        
    def queue_vehicle(self, arriving_vehicle: Vehicle.Vehicle) -> None:
        """
        Adds a vehicle to the queue.
        
        arriving_vehicle: Vehicle.Vehicle
            The vehicle to be added to the queue.
        """
        self.queue.append(arriving_vehicle)
            #self.arrivals += [self.arrivals[-1]+1]
    
class FourWayIntersectionSimulator:
    def __init__(self):
        """
        queue_n : QueueSimulator
            The northbound queue.
        queue_w : QueueSimulator
            The westbound queue.
        queue_s : QueueSimulator
            The southbound queue.
        queue_e : QueueSimulator
            The eastbound queue.
        traffic_light_ns : TrafficLight.PeriodicTrafficLight
            The traffic light controlling the north- and southbound queues.
        traffic_light_ew : TrafficLight.PeriodicTrafficLight
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
        
    def set_queues(self, queue_n=None, queue_w=None, queue_s=None, queue_e=None) -> None:
        """
        Sets the queues of the intersection.
        
        queue_n : QueueSimulator
            The northbound queue.
        queue_w : QueueSimulator
            The westbound queue.
        queue_s : QueueSimulator
            The southbound queue.
        queue_e : QueueSimulator
            The eastbound queue.
        """
        if queue_n != None:
            self.queue_n = queue_n
        if queue_w != None:
            self.queue_w = queue_w
        if queue_s != None:
            self.queue_s = queue_s
        if queue_e != None:
            self.queue_e = queue_e
            
    def set_traffic_lights(self, traffic_light_ns: TrafficLight.PeriodicTrafficLight, traffic_light_ew: TrafficLight.PeriodicTrafficLight) -> None:
        """
        Sets the traffic lights of the intersection.
        
        traffic_light_ns : TrafficLight.PeriodicTrafficLight
            The traffic light controlling the north- and southbound queues.
        traffic_light_ew : TrafficLight.PeriodicTrafficLight
            The traffic light controlling the east- and westbound queues.
        """
        self.traffic_light_ns = traffic_light_ns
        self.traffic_light_ew = traffic_light_ew
        
        self.traffic_light_ns.positions[0] = (self.queue_n.queue.head_position[0]+self.length/2, self.queue_n.queue.head_position[1])
        self.traffic_light_ns.positions[1] = (self.queue_s.queue.head_position[0]-self.length/2, self.queue_s.queue.head_position[1])
        self.traffic_light_ew.positions[0] = (self.queue_e.queue.head_position[0], self.queue_e.queue.head_position[1]-self.length/2)
        self.traffic_light_ew.positions[1] = (self.queue_w.queue.head_position[0], self.queue_w.queue.head_position[1]+self.length/2)
        
        if self.traffic_light_ew.adaptive:
            self.traffic_light_ew.sensor_position = self.position
            
        if self.traffic_light_ns.adaptive:
            self.traffic_light_ns.sensor_position = self.position
        
    def initialize_structure(self, position: (float, float), length=15.) -> None:
        """
        Initializes the structure of the intersection.
        
        position : (float, float)
            The centerpoint of the intersection.
        length : float
            The width of the roads.
        """
        self.position = position
        self.length = length
        
        self.queue_n.head_position = (position[0]+length/4, position[1]-length/2)
        self.queue_w.head_position = (position[0]+length/2, position[1]+length/4)
        self.queue_s.head_position = (position[0]-length/4, position[1]+length/2)
        self.queue_e.head_position = (position[0]-length/2, position[1]-length/4)
        
        self.queue_n.direction = Vehicle.NORTH
        self.queue_w.direction = Vehicle.WEST
        self.queue_s.direction = Vehicle.SOUTH
        self.queue_e.direction = Vehicle.EAST
        
    def initialize_queues(self, avg_departure_time: float, arrival_rate_n=0, arrival_rate_e=0, arrival_rate_s=0, arrival_rate_w=0) -> None:
        """
        Initializes the queues of the intersection.
        
        avg_departure_time : float
            The average time between departures.
        arrival_rate_n : float (optional)
            The average time between arrivals to the northbound queue. Defaults to infinity.
        arrival_rate_w : float (optional)
            The average time between arrivals to the westbound queue. Defaults to infinity.
        arrival_rate_s : float (optional)
            The average time between arrivals to the southbound queue. Defaults to infinity.
        arrival_rate_e : float (optional)
            The average time between arrivals to the eastbound queue. Defaults to infinity.
        """
        self.queue_n.initialize(arrival_rate=arrival_rate_n, avg_departure_time=avg_departure_time, direction=self.queue_n.direction, head_position=self.queue_n.head_position)
        self.queue_w.initialize(arrival_rate=arrival_rate_w, avg_departure_time=avg_departure_time, direction=self.queue_w.direction, head_position=self.queue_w.head_position)
        self.queue_s.initialize(arrival_rate=arrival_rate_s, avg_departure_time=avg_departure_time, direction=self.queue_s.direction, head_position=self.queue_s.head_position)
        self.queue_e.initialize(arrival_rate=arrival_rate_e, avg_departure_time=avg_departure_time, direction=self.queue_e.direction, head_position=self.queue_e.head_position)
        
    def run_event(self, delta_t: float, animate=False, plt=None) -> list:
        """
        Runs all events (arrivals/departures) given the current circumstances and elapses time.
        
        delta_t : float
            The time-step size.
        """
        self.num_queued_vehicles += [self.queue_n.queue.queue_length+self.queue_e.queue.queue_length+self.queue_s.queue.queue_length+self.queue_w.queue.queue_length]
        if self.arrivals > 0:
            self.arrivals_on_green_rate = self.arrivals_on_green/self.arrivals
        
        num_cycles_ns, switches_ns = self.traffic_light_ns.num_cycles, self.traffic_light_ns.switches
        
        if len(num_cycles_ns) > 0 and num_cycles_ns[-1] > 1 and switches_ns[-1] > 0:
            #print(self.time, self.traffic_light_ns.time)
            switch_inds = list(np.array(range(int(round(self.time/delta_t,3))+1))[list(map(lambda x: True if x>0 else False, switches_ns))])
            duration = delta_t*(switch_inds[-1]-switch_inds[-2])
            growth = self.num_queued_vehicles[switch_inds[-1]]-self.num_queued_vehicles[switch_inds[-2]]
            self.cum_clearance_rate_ns += growth/duration
             
        if len(num_cycles_ns) > 0 and num_cycles_ns[-1] > 2:
            self.avg_clearance_rate_ns = self.cum_clearance_rate_ns/(num_cycles_ns[-1]-1)
        
        num_cycles_ew, switches_ew = self.traffic_light_ew.num_cycles, self.traffic_light_ew.switches
        
        if len(num_cycles_ew) > 0 and num_cycles_ew[-1] > 1 and switches_ew[-1] > 0:
            switch_inds = list(np.array(range(int(round(self.time/delta_t,3))+1))[list(map(lambda x: True if x>0 else False, switches_ew))])
            duration = delta_t*(switch_inds[-1]-switch_inds[-2])
            growth = self.num_queued_vehicles[switch_inds[-1]]-self.num_queued_vehicles[switch_inds[-2]]
            self.cum_clearance_rate_ew += growth/duration
            
        if len(num_cycles_ew) > 0 and num_cycles_ew[-1] > 2:
            self.avg_clearance_rate_ew = self.cum_clearance_rate_ew/(num_cycles_ew[-1]-1)
            
        tot_wait_time = self.queue_n.tot_wait_time+self.queue_e.tot_wait_time+self.queue_s.tot_wait_time+self.queue_w.tot_wait_time
        departures = self.queue_n.departures[-1]+self.queue_e.departures[-1]+self.queue_s.departures[-1]+self.queue_w.departures[-1]
        
        if departures > 0:
            self.avg_wait_time = tot_wait_time/departures
        
        horizontal_crossers = []
        for vehicle in self.horizontal_crossers:
            if (vehicle.direction == Vehicle.EAST and vehicle.tail_position[0] < self.queue_w.queue.head_position[0]) or (vehicle.direction == Vehicle.WEST and vehicle.tail_position[0] > self.queue_e.queue.head_position[0]):
                horizontal_crossers += [vehicle]
    
        self.horizontal_crossers = horizontal_crossers
        h_free = 1
        if len(horizontal_crossers) > 0:
            h_free = 0
            
        vertical_crossers = []
        for vehicle in self.vertical_crossers:
            if (vehicle.direction == Vehicle.NORTH and vehicle.tail_position[1] < self.queue_s.queue.head_position[1]) or (vehicle.direction == Vehicle.SOUTH and vehicle.tail_position[1] > self.queue_n.queue.head_position[1]):
                vertical_crossers += [vehicle]
        
        self.vertical_crossers = vertical_crossers
        v_free = 1
        if len(vertical_crossers) > 0:
            #plt.text("busy")
            v_free = 0
        
        arrivals = []
        departures = []
        
        arriving_vehicle_n, departing_vehicle_n = self.queue_n.run_event(delta_t=delta_t, saturation_rate=self.traffic_light_ns.saturation_rate(delta_t=delta_t)*h_free, animate=animate, plt=plt)
        arriving_vehicle_w, departing_vehicle_w = self.queue_w.run_event(delta_t=delta_t, saturation_rate=self.traffic_light_ew.saturation_rate(delta_t=delta_t)*v_free, animate=animate, plt=plt)
        arriving_vehicle_s, departing_vehicle_s = self.queue_s.run_event(delta_t=delta_t, saturation_rate=self.traffic_light_ns.saturation_rate(delta_t=delta_t)*h_free, animate=animate, plt=plt)
        arriving_vehicle_e, departing_vehicle_e = self.queue_e.run_event(delta_t=delta_t, saturation_rate=self.traffic_light_ew.saturation_rate(delta_t=delta_t)*v_free, animate=animate, plt=plt)
        
        if departing_vehicle_n != None:
            departures += [departing_vehicle_n]
            self.vertical_crossers += [departing_vehicle_n] 
            
        if departing_vehicle_w != None:
            departures += [departing_vehicle_w]
            self.horizontal_crossers += [departing_vehicle_w]
            
        if departing_vehicle_s != None:
            departures += [departing_vehicle_s]
            self.vertical_crossers += [departing_vehicle_s]
            
        if departing_vehicle_e != None:
            departures += [departing_vehicle_e]
            self.horizontal_crossers += [departing_vehicle_e]
            
        if arriving_vehicle_n != None:
            arrivals += [arriving_vehicle_n]
            self.arrivals += 1
            
            if self.traffic_light_ns.saturation_rate() > 0:
                self.arrivals_on_green += 1
            
        if arriving_vehicle_w != None:
            arrivals += [arriving_vehicle_w]
            self.arrivals += 1
            
            if self.traffic_light_ew.saturation_rate() > 0:
                self.arrivals_on_green += 1
            
        if arriving_vehicle_s != None:
            arrivals += [arriving_vehicle_s]
            self.arrivals += 1
            
            if self.traffic_light_ns.saturation_rate() > 0:
                self.arrivals_on_green += 1
            
        if arriving_vehicle_e != None:
            arrivals += [arriving_vehicle_e]
            self.arrivals += 1
            
            if self.traffic_light_ew.saturation_rate() > 0:
                self.arrivals_on_green += 1
        
        self.traffic_light_ns.time_step(delta_t=delta_t)
        self.traffic_light_ew.time_step(delta_t=delta_t)
        self.time = self.queue_n.time
        
        if animate:
            if None in self.traffic_light_ns.visuals:
                self.traffic_light_ns.initialize_plot(plt=plt)
            self.traffic_light_ns.update_plot()
            if None in self.traffic_light_ew.visuals:
                self.traffic_light_ew.initialize_plot(plt=plt)
            self.traffic_light_ew.update_plot()
            
            if self.queue_n.visual == None:
                self.queue_n.initialize_plot(position=(self.queue_n.queue.head_position[0]+40,self.queue_n.queue.head_position[1]-20), plt=plt)
            self.queue_n.update_plot()
            if self.queue_w.visual == None:
                self.queue_w.initialize_plot(position=(self.queue_w.queue.head_position[0]+20,self.queue_w.queue.head_position[1]+40), plt=plt)
            self.queue_w.update_plot()
            if self.queue_s.visual == None:
                self.queue_s.initialize_plot(position=(self.queue_s.queue.head_position[0]-40,self.queue_s.queue.head_position[1]+20), plt=plt)
            self.queue_s.update_plot()
            if self.queue_e.visual == None:
                self.queue_e.initialize_plot(position=(self.queue_e.queue.head_position[0]-20,self.queue_e.queue.head_position[1]-40), plt=plt)
            self.queue_e.update_plot()
            
        return arrivals, departures
        
class IntersectionNetworkSimulator:
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
        self.edge_type = None
        self.intersection_type = None
        self.intersections = None
        self.grid_inds = []
        self.vehicles = set()
        self.time = 0.
        self.tot_wait_time = 0.
        self.exits = [0]
        self.observations = []
        self.avg_wait_time = 0.
        self.observable_intersection_grid_inds = []
        
    def initialize(self, grid_dimensions: (int,int), grid_distance=150):
        """
        Initializes the IntersectionNetworkSimulator instance.
        
        grid_dimensions : (int,int)
            The grid dimensions of the intersection network.
        grid_distance : float
            The distance [m] between each intersection centerpoint.
        """
        self.grid_dimensions = grid_dimensions
        self.intersections = np.empty(shape=grid_dimensions, dtype=FourWayIntersectionSimulator)
        self.grid_distance = grid_distance
        
        grid_row_inds = np.concatenate([[i]*grid_dimensions[1] for i in range(grid_dimensions[0])])
        grid_col_inds = list(range(grid_dimensions[1]))*grid_dimensions[0]
        grid_inds = list(zip(grid_row_inds,grid_col_inds))
        self.grid_inds = grid_inds
        
        for grid_ind in grid_inds:
            self.intersections[grid_ind] = self.intersection_type()
            if grid_ind[0] == 0: # upper edge
                self.intersections[grid_ind].set_queues(queue_s=self.edge_type())
            if grid_ind[0] == grid_dimensions[0]-1: # lower edge
                self.intersections[grid_ind].set_queues(queue_n=self.edge_type())
            if grid_ind[1] == 0: # left edge
                self.intersections[grid_ind].set_queues(queue_e=self.edge_type())
            if grid_ind[1] == grid_dimensions[1]-1: # right edge
                self.intersections[grid_ind].set_queues(queue_w=self.edge_type())
                
            self.intersections[grid_ind].initialize_structure(position=(grid_ind[1]*grid_distance, -grid_ind[0]*grid_distance))
    
    def set_queue_rate_parameters(self, grid_ind: (int,int), avg_departure_time: float, arrival_rate_n=0, arrival_rate_w=0, arrival_rate_s=0, arrival_rate_e=0) -> None:
        """
        Sets the departure/arrival rates of the queues within the intersection.
        
        grid_ind : (int,int)
            The grid index of the intersection.
        avg_departure_rate : float
            The average time [s] between departures.
        arrival_rate_n : float (optional)
            The average time [s] between arrivals to the northbound queue. Defaults to infinity.
        arrival_rate_w : float (optional)
            The average time [s] between arrivals to the westbound queue. Defaults to infinity.
        arrival_rate_s : float (optional)
            The average time [s] between arrivals to the southbound queue. Defaults to infinity.
        arrival_rate_e : float (optional)
            The average time [s] between arrivals to the eastbound queue. Defaults to infinity.
        """
        self.intersections[grid_ind].initialize_queues(avg_departure_time=avg_departure_time, arrival_rate_n=arrival_rate_n, arrival_rate_w=arrival_rate_w, arrival_rate_s=arrival_rate_s, arrival_rate_e=arrival_rate_e)
    
    def set_traffic_lights(self, grid_ind: (int,int), traffic_light_ns: TrafficLight.TrafficLight, traffic_light_ew: TrafficLight.TrafficLight) -> None:
        """
        Sets the traffic lights of the intersection.
        
        grid_ind : (int,int)
            The grid index of the intersection.
        traffic_light_ns : TrafficLight.PeriodicTrafficLight
            The traffic light controlling the north- and southbound queues.
        traffic_light_ew : TrafficLight.PeriodicTrafficLight
            The traffic light controlling the east- and westbound queues.
        """
        self.intersections[grid_ind].set_traffic_lights(traffic_light_ns=traffic_light_ns, traffic_light_ew=traffic_light_ew)
        
    def set_observable_intersections(self, grid_inds: [(int,int)]) -> None:
        self.observable_intersection_grid_inds = grid_inds
        
        for grid_ind in grid_inds:
            self.intersections[grid_ind].observable = True
            
        unobservable = set(self.grid_inds)-set(grid_inds)   
        for grid_ind in unobservable:
            self.intersections[grid_ind].estimator = FourWayIntersectionEstimator()
            self.intersections[grid_ind].estimator.initialize(intersection=self.intersections[grid_ind])
            
    def reset(self):
        network = IntersectionNetworkSimulator()
        network.edge_type = self.edge_type
        network.intersection_type = self.intersection_type
        network.initialize(grid_dimensions=self.grid_dimensions, grid_distance=self.grid_distance)
        
        for grid_ind in self.grid_inds:
            intersection = self.intersections[grid_ind]
                
            network.set_queue_rate_parameters(grid_ind=grid_ind, avg_departure_time=1/intersection.queue_n.queue.departure_rate, arrival_rate_n=intersection.queue_n.queue.arrival_rate, arrival_rate_w=intersection.queue_w.queue.arrival_rate, arrival_rate_s=intersection.queue_s.queue.arrival_rate, arrival_rate_e=intersection.queue_e.queue.arrival_rate)
            
            traffic_light_ns = intersection.traffic_light_ns.reset()
            traffic_light_ew = intersection.traffic_light_ew.reset()
            network.set_traffic_lights(grid_ind=grid_ind, traffic_light_ns=traffic_light_ns, traffic_light_ew=traffic_light_ew)
            
        network.set_observable_intersections(grid_inds=self.observable_intersection_grid_inds)
        
        return network
        
    def initialize_plot(self, fig_size, plt):
        fig, ax = plt.subplots(figsize=fig_size, dpi=90)
        ax.axis('equal')
        ax.set(xlim=(-50,(self.grid_dimensions[1]-1)*self.grid_distance+50), ylim=(-(self.grid_dimensions[0]-1)*self.grid_distance-50,50))
        
        x_lim = ax.get_xlim()
        y_lim = ax.get_ylim()
        x = np.arange(ax.get_xlim()[0], ax.get_xlim()[1], 0.25)
        y = np.arange(ax.get_ylim()[0], ax.get_ylim()[1], 0.25)
        for grid_ind in self.grid_inds:
            intersection = self.intersections[grid_ind]
            if grid_ind[0] == 0:
                ax.fill_between(x, y_lim[0], y_lim[1], where=(x >= intersection.position[0]-intersection.length/2) & (x <= intersection.position[0]+intersection.length/2), facecolor='0.5', alpha=0.4)
                ax.plot([intersection.position[0], intersection.position[0]], [y_lim[0], y_lim[1]], 'w--')
            if grid_ind[1] == 0:
                ax.fill_betweenx(y, x_lim[0], x_lim[1], where=(y >= intersection.position[1]-intersection.length/2) & (y <= intersection.position[1]+intersection.length/2), facecolor='0.5', alpha=0.4)
                ax.plot([x_lim[0], x_lim[1]], [intersection.position[1], intersection.position[1]], 'w--')
        
        return fig, ax

    def simulate(self, delta_t: float, end_time: float, fig_width=4, animate=False, file_name="simulation.mp4", output_destination="../data/vids/", speed=1) -> None:
        if animate:
            FFMpegWriter = manimation.writers['ffmpeg']
            metadata = dict(title='Simulation', artist='Matplotlib',
                            comment='Visual representation of the simulation.')
            fps = int(speed/delta_t)
            writer = FFMpegWriter(fps=fps, metadata=metadata)
            
            fig_height = fig_width*self.grid_dimensions[0]/self.grid_dimensions[1]
            fig, ax = self.initialize_plot((fig_width, fig_height), plt)
            text = plt.gcf().text(0, 0.95, "Elapsed time: 0s", fontsize=14)

            with writer.saving(fig, Path(output_destination) / file_name, 100):
                while self.time < end_time:
                    self.run_event(delta_t=delta_t, animate=True, plt=plt)
                    text.set_text("Elapsed time: "+str(round(self.time,1))+"s")
                    writer.grab_frame()
        else:
            while self.time < end_time:
                self.run_event(delta_t=delta_t)
        
    def run_event(self, delta_t: float, animate=False, plt=None) -> (dict,dict):
        """
        Runs all events (departures/arrivals) given the current circumstances and elapses time.
        
        delta_t : float
            The time-step size.
        """
        self.exits += [self.exits[-1]]
        exits = []
        
        for vehicle in self.vehicles:
            if self.out_of_bounds(vehicle):
                exits += [vehicle]
                self.exits[-1] += 1
                self.tot_wait_time += vehicle.tot_wait_time
                
                if animate:
                    vehicle.remove_plot()
                continue
                
            if animate:
                if vehicle.visual == None:
                    vehicle.initialize_plot(plt, linewidth=4.5/math.log(math.sqrt(5*len(self.grid_inds))))
                vehicle.update_plot()
            
            if vehicle.destination in self.grid_inds and vehicle.speed > 0 and self.distance_to_destination(vehicle=vehicle) < (2 + vehicle.full_speed*delta_t):
                if vehicle.direction == Vehicle.NORTH:
                    self.intersections[vehicle.destination].queue_n.queue_vehicle(arriving_vehicle=vehicle)
                elif vehicle.direction == Vehicle.WEST:
                    self.intersections[vehicle.destination].queue_w.queue_vehicle(arriving_vehicle=vehicle)
                elif vehicle.direction == Vehicle.SOUTH:
                    self.intersections[vehicle.destination].queue_s.queue_vehicle(arriving_vehicle=vehicle)
                elif vehicle.direction == Vehicle.EAST:
                    self.intersections[vehicle.destination].queue_e.queue_vehicle(arriving_vehicle=vehicle) 
        
        if self.exits[-1] > 0:
            self.avg_wait_time = self.tot_wait_time/self.exits[-1]
        
        for exit in exits:
            self.vehicles.remove(exit)
        
        arrivals = dict()
        departures = dict()
        
        for grid_ind in self.grid_inds:
            intersection_arrivals, intersection_departures = self.intersections[grid_ind].run_event(delta_t=delta_t, animate=animate, plt=plt)
            arrivals[grid_ind] = intersection_arrivals
            for arrival in intersection_arrivals:
                arrival.destination = grid_ind
                self.vehicles.add(arrival)
            
            intersection_departures = [(departure,grid_ind) for departure in intersection_departures]
            departures[grid_ind] = self.update_destinations(intersection_departures)
            
            if self.intersections[grid_ind].observable:
                self.observe(departures=departures[grid_ind])
        
        for grid_ind in self.grid_inds:
            northbound = []
            eastbound = []
            southbound = []
            westbound = []
                
            if self.intersections[grid_ind].traffic_light_ew.adaptive or self.intersections[grid_ind].traffic_light_ns.adaptive:
                vehicles = list(filter(lambda vehicle: vehicle.destination == grid_ind, self.vehicles))
                northbound = list(filter(lambda vehicle: vehicle.direction == Vehicle.NORTH, vehicles))
                eastbound = list(filter(lambda vehicle: vehicle.direction == Vehicle.EAST, vehicles))
                southbound = list(filter(lambda vehicle: vehicle.direction == Vehicle.SOUTH, vehicles))
                westbound = list(filter(lambda vehicle: vehicle.direction == Vehicle.WEST, vehicles))
                
                #print(grid_ind, len(vehicles), len(northbound), len(eastbound), len(southbound), len(westbound))
                
            if self.intersections[grid_ind].traffic_light_ew.adaptive:
                self.intersections[grid_ind].traffic_light_ew.sense(queue_1=eastbound, queue_2=westbound, opposite_queue_1=northbound, opposite_queue_2=southbound)
            
            if self.intersections[grid_ind].traffic_light_ns.adaptive:
                self.intersections[grid_ind].traffic_light_ns.sense(queue_1=northbound, queue_2=southbound, opposite_queue_1=eastbound, opposite_queue_2=westbound)
                
            if not self.intersections[grid_ind].observable:
                self.observations = self.intersections[grid_ind].estimator.estimate(observations=self.observations)
                self.intersections[grid_ind].estimator.run_event(delta_t=delta_t)
        
        for vehicle in self.vehicles:
            vehicle.time_step(delta_t=delta_t)
            
        self.time = self.intersections[(0,0)].time
        
        return arrivals, departures
    
    def observe(self, departures) -> None:
        self.observations += [{"position": vehicle.position, "direction": vehicle.direction, "speed": vehicle.speed, "destination": self.intersections[vehicle.destination]} if vehicle.destination in self.grid_inds else {} for vehicle in departures]
            
    def update_destinations(self, departures: list) -> list:
        """
        Updates the destinations of departing vehicles.
        
        departures : [(Vehicle.Vehicle, (int,int))]
            The departures and the grid indices they are departing from.
        """
        moving_vehicles = []
        
        for departing_vehicle,prev_pos in departures:
            if departing_vehicle.direction == Vehicle.NORTH:
                departing_vehicle.destination = (prev_pos[0]-1, prev_pos[1])
                
                if departing_vehicle.destination in self.grid_inds:
                    self.intersections[departing_vehicle.destination].queue_n.adjust_position(departing_vehicle)
                        
            elif departing_vehicle.direction == Vehicle.WEST:
                departing_vehicle.destination = (prev_pos[0], prev_pos[1]-1)
                
                if departing_vehicle.destination in self.grid_inds:
                    self.intersections[departing_vehicle.destination].queue_w.adjust_position(departing_vehicle)
                    
            elif departing_vehicle.direction == Vehicle.SOUTH:
                departing_vehicle.destination = (prev_pos[0]+1, prev_pos[1])
                
                if departing_vehicle.destination in self.grid_inds:
                    self.intersections[departing_vehicle.destination].queue_s.adjust_position(departing_vehicle)
                    
            elif departing_vehicle.direction == Vehicle.EAST:
                departing_vehicle.destination = (prev_pos[0], prev_pos[1]+1)
                
                if departing_vehicle.destination in self.grid_inds:
                    self.intersections[departing_vehicle.destination].queue_e.adjust_position(departing_vehicle)
            
            moving_vehicles += [departing_vehicle]
                
        return moving_vehicles
    
    def out_of_bounds(self, vehicle: Vehicle.Vehicle) -> bool:
        """
        Checks if the vehicle has exited the network.
        
        vehicle : Vehicle.Vehicle
            The vehicle being checked.
        """
        if vehicle.direction == Vehicle.NORTH and vehicle.tail_position[1] > (self.intersections[(0,0)].queue_s.queue.head_position[1]+50):
            return True
        elif vehicle.direction == Vehicle.WEST and vehicle.tail_position[0] < (self.intersections[(0,0)].queue_e.queue.head_position[0]-50):
            return True
        elif vehicle.direction == Vehicle.SOUTH and vehicle.tail_position[1] < (self.intersections[self.grid_inds[-1]].queue_n.queue.head_position[1]-50):
            return True
        elif vehicle.direction == Vehicle.EAST and vehicle.tail_position[0] > (self.intersections[self.grid_inds[-1]].queue_w.queue.head_position[0]+50):
            return True
        
        return False
    
    def distance_to_destination(self, vehicle: Vehicle.Vehicle):
        """
        Returns the distance [m] to the vehicle's destination.
        
        vehicle : Vehicle.Vehicle
            The vehicle being checked.
        """
        destination_x = 0
        destination_y = 0
        passed = 1
        
        if vehicle.direction == Vehicle.NORTH:
            destination_x = self.intersections[vehicle.destination].queue_n.queue.tail_position[0]
            destination_y = self.intersections[vehicle.destination].queue_n.queue.tail_position[1]
            
            if vehicle.position[1] > destination_y:
                passed = -1
                
        elif vehicle.direction == Vehicle.WEST:
            destination_x = self.intersections[vehicle.destination].queue_w.queue.tail_position[0]
            destination_y = self.intersections[vehicle.destination].queue_w.queue.tail_position[1]
            
            if vehicle.position[0] < destination_x:
                passed = -1
                
        elif vehicle.direction == Vehicle.SOUTH:
            destination_x = self.intersections[vehicle.destination].queue_s.queue.tail_position[0]
            destination_y = self.intersections[vehicle.destination].queue_s.queue.tail_position[1]
            
            if vehicle.position[1] < destination_y:
                passed = -1
                
        elif vehicle.direction == Vehicle.EAST:
            destination_x = self.intersections[vehicle.destination].queue_e.queue.tail_position[0]
            destination_y = self.intersections[vehicle.destination].queue_e.queue.tail_position[1]
            
            if vehicle.position[0] > destination_x:
                passed = -1
        
        return passed*math.hypot(destination_x-vehicle.position[0], destination_y-vehicle.position[1])
    
    def get_stats(self) -> dict:
        """
        Returns all the simulation stats.
        """
        stats = {}
        
        for grid_ind in self.grid_inds:
            n_queue_length, n_departures, n_arrivals, n_wait_time = self.intersections[grid_ind].queue_n.get_stats()
            w_queue_length, w_departures, w_arrivals, w_wait_time = self.intersections[grid_ind].queue_w.get_stats()
            s_queue_length, s_departures, s_arrivals, s_wait_time = self.intersections[grid_ind].queue_s.get_stats()
            e_queue_length, e_departures, e_arrivals, e_wait_time = self.intersections[grid_ind].queue_e.get_stats()
            
            
            
            stats[grid_ind] = {}
            stats[grid_ind]["num_queued_vehicles"] = self.intersections[grid_ind].num_queued_vehicles[1:]
            stats[grid_ind]["avg_clearance_rate_ns"] = self.intersections[grid_ind].avg_clearance_rate_ns
            stats[grid_ind]["avg_clearance_rate_ew"] = self.intersections[grid_ind].avg_clearance_rate_ew
            stats[grid_ind]["arrivals_on_green_rate"] = self.intersections[grid_ind].arrivals_on_green_rate
            
            stats[grid_ind]["N"] = {}
            stats[grid_ind]["N"]["queue_length"] = n_queue_length
            stats[grid_ind]["N"]["arrivals"] = n_arrivals
            stats[grid_ind]["N"]["departures"] = n_departures
            stats[grid_ind]["N"]["wait_time"] = n_wait_time
            stats[grid_ind]["N"]["avg_queue_length"] = sum(n_queue_length)/len(n_queue_length)

            stats[grid_ind]["W"] = {}
            stats[grid_ind]["W"]["queue_length"] = w_queue_length
            stats[grid_ind]["W"]["arrivals"] = w_arrivals
            stats[grid_ind]["W"]["departures"] = w_departures
            stats[grid_ind]["W"]["wait_time"] = w_wait_time
            stats[grid_ind]["W"]["avg_queue_length"] = sum(w_queue_length)/len(w_queue_length)
            
            stats[grid_ind]["S"] = {}
            stats[grid_ind]["S"]["queue_length"] = s_queue_length
            stats[grid_ind]["S"]["arrivals"] = s_arrivals
            stats[grid_ind]["S"]["departures"] = s_departures
            stats[grid_ind]["S"]["wait_time"] = s_wait_time
            stats[grid_ind]["S"]["avg_queue_length"] = sum(s_queue_length)/len(s_queue_length)

            stats[grid_ind]["E"] = {}
            stats[grid_ind]["E"]["queue_length"] = e_queue_length
            stats[grid_ind]["E"]["arrivals"] = e_arrivals
            stats[grid_ind]["E"]["departures"] = e_departures
            stats[grid_ind]["E"]["wait_time"] = e_wait_time
            stats[grid_ind]["E"]["avg_queue_length"] = sum(e_queue_length)/len(e_queue_length)
            
            stats["avg_wait_time"] = self.avg_wait_time
            
        return stats
    
    def save_to_file(self, file_name: str, output_destination="./data/") -> None:
        f = open(Path(output_destination) / file_name,"wb")
        pkl.dump(self,f)
        f.close()
    
    def plot_queue_stats(self, plt, grid_ind: (int,int), direction: (int,int), end_time: float, delta_t: float, fig_size=(float,float), start_time=0, traffic_light=None):
        """
        Plots the simulation stats for a queue.
        
        plt : matplotlib.pyplot
            The pyplot instance used for plotting.
        grid_ind : (int,int)
            The grid index of the queue.
        direction : (int,int)
            The travel direction of the queue.
        end_time : float
            The end time [s] of the plot.
        delta_t : float
            The time-step size.
        fig_size : (float, float)
            The figure size of the plot.
        start_time : (float, float) (optional)
            The start time [s] of the plot. Defaults to 0.
        traffic_light : TrafficLight.PeriodicTrafficLight (optional)
            The traffic light controlling the queue.
        """
        fig, axs = plt.subplots(3, figsize=fig_size, dpi=90, sharex=True)
        queue_data = self.get_stats()[grid_ind][direction]
        estimated_queue_data = None
        if not self.intersections[grid_ind].observable:
            estimated_queue_data = self.intersections[grid_ind].estimator.get_stats()[direction]
        
        t = np.arange(start_time,end_time,delta_t)
        
        start_ind = int(start_time/delta_t)
        end_ind = int(end_time/delta_t)
        
        axs[0].plot(t, queue_data['queue_length'][start_ind:end_ind], 'black', label="Simulated")
        if estimated_queue_data != None:
            axs[0].plot(t, estimated_queue_data['queue_length'][start_ind:end_ind], color='black', linestyle='--', label="Estimated")
            axs[0].legend()
        axs[0].set(ylabel='nbr. of vehicles')
        axs[0].set_title('Queue length')
        axs[0].yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        axs[0].label_outer()
        
        axs[1].plot(t, queue_data['arrivals'][start_ind:end_ind], 'black')
        if estimated_queue_data != None:
            axs[1].plot(t, estimated_queue_data['arrivals'][start_ind:end_ind], color='black', linestyle='--')
        axs[1].set(ylabel='nbr. of vehicles')
        axs[1].set_title('Total nbr. of arrivals')
        axs[1].yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        axs[1].label_outer()
        
        axs[2].plot(t, queue_data['departures'][start_ind:end_ind], 'black')
        if estimated_queue_data != None:
            axs[2].plot(t, estimated_queue_data['departures'][start_ind:end_ind], color='black', linestyle='--')
        axs[2].set(xlabel='time [s]', ylabel='nbr. of vehicles')
        axs[2].set_title('Total nbr. of departures')
        axs[2].yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        axs[2].label_outer()

        if traffic_light != None:
            traffic_light.plot_green_light(axs[0],t)
            traffic_light.plot_green_light(axs[2],t)

        return fig, axs
    
    def plot_avg_clearance_rate(self, plt, grid_ind: (int,int), end_time: float, delta_t: float, fig_size=(float,float), start_time=0):
        """
        Plots the simulation stats for a queue.
        
        plt : matplotlib.pyplot
            The pyplot instance used for plotting.
        grid_ind : (int,int)
            The grid index of the queue.
        direction : (int,int)
            The travel direction of the queue.
        end_time : float
            The end time [s] of the plot.
        delta_t : float
            The time-step size.
        fig_size : (float, float)
            The figure size of the plot.
        start_time : (float, float) (optional)
            The start time [s] of the plot. Defaults to 0.
        traffic_light : TrafficLight.PeriodicTrafficLight (optional)
            The traffic light controlling the queue.
        """
        fig, ax = plt.subplots(figsize=fig_size, dpi=90)
        rate_ns = self.get_stats()[grid_ind]["avg_clearance_rate_ns"]
        rate_ew = self.get_stats()[grid_ind]["avg_clearance_rate_ew"]
        
        t = np.arange(start_time,end_time,delta_t)
        
        start_ind = int(start_time/delta_t)
        end_ind = int(end_time/delta_t)
        
        ax.plot(t, rate_ns[start_ind:end_ind], label="NS")
        ax.plot(t, rate_ew[start_ind:end_ind], label="EW")
        ax.set(xlabel="time [s]", ylabel='avg. clearance rate')
        ax.set_title('Average clearance rate over time')
        ax.label_outer()
        ax.legend()

        return fig, ax
    
    def plot_avg_wait_time(self, plt, end_time: float, delta_t: float, fig_size=(float,float), start_time=0):
        fig, ax = plt.subplots(figsize=fig_size, dpi=90)
        
        t = np.arange(start_time,end_time,delta_t)
        
        start_ind = int(start_time/delta_t)
        end_ind = int(end_time/delta_t)
        
        ax.plot(t, self.avg_wait_time[start_ind:end_ind], 'black')
        ax.set(xlabel='time [s]', ylabel='avg. wait time [s]')
        ax.set_title('Average wait time over time')
        ax.label_outer()
        
        return fig, ax
    
class QueueEstimator():
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
        next_arrival_timestamp : float
            The timestamp at which the next arrival occurs.
        next_time_to_depart : float
            The time between the last departure and the next [s].
        """
        self.time = 0
        self.arrival_timestamps = []
        self.time_served = 0
        self.queue_length = [0]
        self.departures = [0]
        self.arrivals = [0]
        self.external_arrivals = False
        self.head_position = (0.,0.)
        self.tail_position = (0.,0.)
        self.direction = (0,0)
        
    def initialize(self, direction=Vehicle.NORTH, head_position=(0.,0.), external_arrivals=False) -> None:
        """
        Initializes the QueueSimulator instance.
        
        arrival_rate (optional) : float
            The average time [s] between arrivals to the queue. Defaults to infinity.
        avg_departure_time (optional): float
            The average time [s] between departures from the queue. Defaults to infinity.
        direction : (float, float) (optional)
            Travel direction of this queue. Defaults to Vehicle.NORTH.
        head_position : (float, float) (optional)
            Position of the queue's head. Defaults to (0.,0.).
        """
        self.direction = direction
        self.head_position = head_position
        self.tail_position = head_position
        self.external_arrivals = external_arrivals
        
    def time_step(self, delta_t: float) -> None:
        """
        Elapses time by one time-step.
        
        delta_t : float
            The time-step size.
        """
        self.time += delta_t
        self.time_served += delta_t
        
    def run_event(self, delta_t: float, saturation_rate: float) -> None:
        arrival, departure = 0, 0
        
        if self.external_arrivals and len(self.arrival_timestamps) <= 0:
            self.arrival_timestamps += [self.time+np.random.normal(loc=10, scale=5)]
                
        
        if len(self.arrival_timestamps) > 0 and self.time >= self.arrival_timestamps[0]:
            arrival = 1
            self.arrivals += [self.arrivals[-1]+1]
            self.arrival_timestamps = self.arrival_timestamps[1:]
        else:
            self.arrivals += [self.arrivals[-1]]
        
        if saturation_rate <= 0:
            self.time_served = 0
        
        if self.queue_length[-1] > 0:
            if self.time_served >= 2:
                departure = 1
                self.departures += [self.departures[-1]+1]
                self.time_served = 0
            else:
                self.departures += [self.departures[-1]]
        else:
            self.time_served = 0
            self.departures += [self.departures[-1]]
            
        self.queue_length += [self.queue_length[-1]+arrival-departure]
        self.update_tail_position()
        
        self.time_step(delta_t=delta_t)
        
    def update_tail_position(self) -> None:
        tot_length = self.queue_length[-1]*5
        self.tail_position = (self.head_position[0]-self.direction[0]*tot_length, self.head_position[1]-self.direction[1]*tot_length)
    
    def get_stats(self) -> (list, list, list, float):
        """
        Returns stats.
        """
        return self.queue_length[1:], self.departures[1:], self.arrivals[1:]

class FourWayIntersectionEstimator:
    def __init__(self):
        """
        queue_n : QueueSimulator
            The northbound queue.
        queue_w : QueueSimulator
            The westbound queue.
        queue_s : QueueSimulator
            The southbound queue.
        queue_e : QueueSimulator
            The eastbound queue.
        traffic_light_ns : TrafficLight.PeriodicTrafficLight
            The traffic light controlling the north- and southbound queues.
        traffic_light_ew : TrafficLight.PeriodicTrafficLight
            The traffic light controlling the east- and westbound queues.
        position : (float, float)
            The centerpoint of the intersection.
        length : float
            The width of the roads.
        time : float
            The current simulation time [s].
        """
        self.queue_n = QueueEstimator()
        self.queue_w = QueueEstimator()
        self.queue_s = QueueEstimator()
        self.queue_e = QueueEstimator()
        self.traffic_light_ns = None
        self.traffic_light_ew = None
        self.position = (0.,0.)
        self.length = 0.
        self.time = 0.
        
    def initialize(self, intersection: FourWayIntersectionSimulator):
        self.traffic_light_ns = intersection.traffic_light_ns
        self.traffic_light_ew = intersection.traffic_light_ew
        
        self.position = intersection.position
        
        self.queue_n.initialize(head_position=intersection.queue_n.head_position, direction=Vehicle.NORTH, external_arrivals=intersection.queue_n.edge)
        self.queue_w.initialize(head_position=intersection.queue_w.head_position, direction=Vehicle.WEST, external_arrivals=intersection.queue_w.edge)
        self.queue_s.initialize(head_position=intersection.queue_s.head_position, direction=Vehicle.SOUTH, external_arrivals=intersection.queue_s.edge)
        self.queue_e.initialize(head_position=intersection.queue_e.head_position, direction=Vehicle.EAST, external_arrivals=intersection.queue_e.edge)
        
    def time_step(self, delta_t: float):
        self.time += delta_t
        
    def estimate(self, observations: [dict]) -> [dict]:
        updated = []
        
        for observation in observations:
            if observation != {} and observation["destination"].position == self.position:
                queue = None
                
                if observation["direction"] == Vehicle.NORTH:
                    queue = self.queue_n

                elif observation["direction"] == Vehicle.WEST:
                    queue = self.queue_w

                elif observation["direction"] == Vehicle.SOUTH:
                    queue = self.queue_s

                elif observation["direction"] == Vehicle.EAST:
                    queue = self.queue_e
                    
                destination_x = queue.tail_position[0]
                destination_y = queue.tail_position[1]
                time_until_arrival = math.hypot(destination_x-observation["position"][0], destination_y-observation["position"][1])/observation["speed"]
                queue.arrival_timestamps += [queue.time+time_until_arrival]
                
            elif observation != {}:
                updated += [observation]
                
        return updated
        
    def run_event(self, delta_t: float):
        self.queue_n.run_event(delta_t=delta_t, saturation_rate=self.traffic_light_ns.saturation_rate())
        self.queue_e.run_event(delta_t=delta_t, saturation_rate=self.traffic_light_ew.saturation_rate())
        self.queue_s.run_event(delta_t=delta_t, saturation_rate=self.traffic_light_ns.saturation_rate())
        self.queue_w.run_event(delta_t=delta_t, saturation_rate=self.traffic_light_ew.saturation_rate())
        
        self.time_step(delta_t=delta_t)
        
    def get_stats(self) -> dict:
        """
        Returns all the estimation stats.
        """
        stats = {}
        
        n_queue_length, n_departures, n_arrivals = self.queue_n.get_stats()
        w_queue_length, w_departures, w_arrivals = self.queue_w.get_stats()
        s_queue_length, s_departures, s_arrivals = self.queue_s.get_stats()
        e_queue_length, e_departures, e_arrivals = self.queue_e.get_stats()

        stats["N"] = {}
        stats["N"]["queue_length"] = n_queue_length
        stats["N"]["arrivals"] = n_arrivals
        stats["N"]["departures"] = n_departures

        stats["W"] = {}
        stats["W"]["queue_length"] = w_queue_length
        stats["W"]["arrivals"] = w_arrivals
        stats["W"]["departures"] = w_departures

        stats["S"] = {}
        stats["S"]["queue_length"] = s_queue_length
        stats["S"]["arrivals"] = s_arrivals
        stats["S"]["departures"] = s_departures

        stats["E"] = {}
        stats["E"]["queue_length"] = e_queue_length
        stats["E"]["arrivals"] = e_arrivals
        stats["E"]["departures"] = e_departures
            
        return stats