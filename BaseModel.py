import random
import numpy as np
import Vehicle
import TrafficLight
import math
import matplotlib.pyplot as plt
import matplotlib.animation as manimation

class BaseQueue:
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
        self.arrival_rate = 0
        self.departure_rate = 0
    
    def initialize(self, avg_departure_time: float, direction: (int, int), head_position: (float, float), avg_arrival_time=np.inf) -> None:
        """
        Initializes the BaseQueue instance.
        
        avg_arrival_time : float (optional)
            The average time [s] between arrivals to the queue. Defaults to infinity.
        avg_departure_time : float
            The average time [s] between departures from the queue.
        direction: (float, float)
            Travel direction of this queue.
        head_position : (float, float)
            Position of the queue's head.
        """
        self.arrival_rate = 1/avg_arrival_time
        self.departure_rate = 1/avg_departure_time
        self.direction = direction
        self.head_position = head_position
        self.tail_position = head_position
    
    def append(self, vehicle: Vehicle.Vehicle) -> None:
        """
        Appends a vehicle to the queue.
        
        vehicle : Vehicle.Vehicle
            The vehicle to be appended to the queue.
        """
        vehicle.stop()
        self.vehicles += [vehicle]
        self.queue_length = len(self.vehicles)
        vehicle.position = self.tail_position
        self.tail_position = (self.tail_position[0]-self.direction[0]*vehicle.length, self.tail_position[1]-self.direction[1]*vehicle.length)
        
    def shift_vehicles(self) -> None:
        """
        Moves each vehicle by one step in the queue, except for the frontmost vehicle.
        """
        old_positions = [vehicle.position for vehicle in self.vehicles]
        
        for i in range(1,self.queue_length):
            self.vehicles[i].position = old_positions[i-1]
        
    def remove(self) -> Vehicle.Vehicle:
        """
        Removes a vehicle from the queue.
        """
        if self.queue_length > 0:
            self.shift_vehicles()
            departing_vehicle = self.vehicles[0]
            self.vehicles = self.vehicles[1:]
            self.queue_length = len(self.vehicles)
            if self.queue_length > 0: 
                self.tail_position = (self.vehicles[-1].position[0]-self.direction[0]*departing_vehicle.length, self.vehicles[-1].position[1]-self.direction[1]*departing_vehicle.length)
            else:
                self.tail_position = self.head_position
                
            return departing_vehicle
        return None
    
class BaseQueueSimulator:
    def __init__(self):
        """
        queue : BaseQueue
            The internal BaseQueue instance.
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
        self.queue = BaseQueue()
        self.time = 0
        self.time_since_arrival = 0
        self.time_served = 0
        self.queue_length = [0]
        self.departures = [0]
        self.arrivals = [0]
        self.tot_wait_time = 0
        self.next_arrival_timestamp = 0
        self.next_time_to_depart = 0
        
    def initialize(self, avg_departure_time=np.inf, avg_arrival_time=np.inf, direction=Vehicle.NORTH, head_position=(0.,0.)) -> None:
        """
        Initializes the BaseQueueSimulator instance.
        
        avg_arrival_time (optional) : float
            The average time [s] between arrivals to the queue. Defaults to infinity.
        avg_departure_time (optional): float
            The average time [s] between departures from the queue. Defaults to infinity.
        direction : (float, float) (optional)
            Travel direction of this queue. Defaults to Vehicle.NORTH.
        head_position : (float, float) (optional)
            Position of the queue's head. Defaults to (0.,0.).
        """
        self.queue.initialize(avg_arrival_time=avg_arrival_time, avg_departure_time=avg_departure_time, direction=direction, head_position=head_position)
        self.next_arrival_timestamp = abs(np.random.normal(loc=avg_arrival_time, scale=0.1*avg_arrival_time))
        self.next_time_to_depart = abs(np.random.normal(loc=avg_departure_time, scale=0.1*avg_departure_time))
        
    def time_step(self, delta_t: float, animate=False, plt=None) -> None:
        """
        Elapses time by one time-step.
        
        delta_t : float
            The time-step size.
        """
        self.time += delta_t
        self.time_since_arrival += delta_t
        self.time_served += delta_t
        
        for vehicle in self.queue.vehicles:
            vehicle.time_step(delta_t=delta_t)
            if animate:
                vehicle.update_plot()
            
    def adjust_position(self, vehicle) -> None:
        """
        Adjusts the position of the vehicle to this queue.
        """
        if self.queue.direction == Vehicle.NORTH:
            vehicle.position = (self.queue.head_position[0], vehicle.position[1])
        elif self.queue.direction == Vehicle.WEST:
            vehicle.position = (vehicle.position[0], self.queue.head_position[1])
        elif self.queue.direction == Vehicle.SOUTH:
            vehicle.position = (self.queue.head_position[0], vehicle.position[1])
        elif self.queue.direction == Vehicle.WEST:
            vehicle.position = (vehicle.position[0], self.queue.head_position[1])
        
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
    
class FourWayIntersectionSimulator:
    def __init__(self):
        """
        queue_n : BaseQueueSimulator
            The northbound queue.
        queue_w : BaseQueueSimulator
            The westbound queue.
        queue_s : BaseQueueSimulator
            The southbound queue.
        queue_e : BaseQueueSimulator
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
        self.queue_n = BaseQueueSimulator()
        self.queue_w = BaseQueueSimulator()
        self.queue_s = BaseQueueSimulator()
        self.queue_e = BaseQueueSimulator()
        self.traffic_light_ns = None
        self.traffic_light_ew = None
        self.position = (0.,0.)
        self.length = 0.
        self.time = 0.
        
    def set_queues(self, queue_n=None, queue_w=None, queue_s=None, queue_e=None) -> None:
        """
        Sets the queues of the intersection.
        
        queue_n : BaseQueueSimulator
            The northbound queue.
        queue_w : BaseQueueSimulator
            The westbound queue.
        queue_s : BaseQueueSimulator
            The southbound queue.
        queue_e : BaseQueueSimulator
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
            
    def set_traffic_lights(self, traffic_light_ns: TrafficLight.SimpleTrafficLight, traffic_light_ew: TrafficLight.SimpleTrafficLight) -> None:
        """
        Sets the traffic lights of the intersection.
        
        traffic_light_ns : TrafficLight.SimpleTrafficLight
            The traffic light controlling the north- and southbound queues.
        traffic_light_ew : TrafficLight.SimpleTrafficLight
            The traffic light controlling the east- and westbound queues.
        """
        self.traffic_light_ns = traffic_light_ns
        self.traffic_light_ew = traffic_light_ew
        
        self.traffic_light_ns.positions[0] = (self.queue_n.queue.head_position[0]+3, self.queue_n.queue.head_position[1]+3)
        self.traffic_light_ns.positions[1] = (self.queue_s.queue.head_position[0]-3, self.queue_s.queue.head_position[1]-3)
        self.traffic_light_ew.positions[0] = (self.queue_e.queue.head_position[0]+3, self.queue_e.queue.head_position[1]-3)
        self.traffic_light_ew.positions[1] = (self.queue_w.queue.head_position[0]-3, self.queue_w.queue.head_position[1]+3)
        
    def initialize_structure(self, position: (float, float), length=30.) -> None:
        """
        Initializes the structure of the intersection.
        
        position : (float, float)
            The centerpoint of the intersection.
        length : float
            The width of the roads.
        """
        self.position = position
        self.queue_n.head_position = (position[0]+3, position[1]-length/2)
        self.queue_w.head_position = (position[0]+length/2, position[1]+3)
        self.queue_s.head_position = (position[0]-3, position[1]+length/2)
        self.queue_e.head_position = (position[0]-length/2, position[1]-3)
        
        self.queue_n.direction = Vehicle.NORTH
        self.queue_w.direction = Vehicle.WEST
        self.queue_s.direction = Vehicle.SOUTH
        self.queue_e.direction = Vehicle.EAST
        
    def initialize_queues(self, avg_departure_time: float, avg_arrival_time_n=np.inf, avg_arrival_time_w=np.inf, avg_arrival_time_s=np.inf, avg_arrival_time_e=np.inf) -> None:
        """
        Initializes the queues of the intersection.
        
        avg_departure_time : float
            The average time between departures.
        avg_arrival_time_n : float (optional)
            The average time between arrivals to the northbound queue. Defaults to infinity.
        avg_arrival_time_w : float (optional)
            The average time between arrivals to the westbound queue. Defaults to infinity.
        avg_arrival_time_s : float (optional)
            The average time between arrivals to the southbound queue. Defaults to infinity.
        avg_arrival_time_e : float (optional)
            The average time between arrivals to the eastbound queue. Defaults to infinity.
        """
        self.queue_n.initialize(avg_arrival_time=avg_arrival_time_n, avg_departure_time=avg_departure_time, direction=self.queue_n.direction, head_position=self.queue_n.head_position)
        self.queue_w.initialize(avg_arrival_time=avg_arrival_time_w, avg_departure_time=avg_departure_time, direction=self.queue_w.direction, head_position=self.queue_w.head_position)
        self.queue_s.initialize(avg_arrival_time=avg_arrival_time_s, avg_departure_time=avg_departure_time, direction=self.queue_s.direction, head_position=self.queue_s.head_position)
        self.queue_e.initialize(avg_arrival_time=avg_arrival_time_e, avg_departure_time=avg_departure_time, direction=self.queue_e.direction, head_position=self.queue_e.head_position)
        
    def run_event(self, delta_t: float, animate=False, plt=None) -> list:
        """
        Runs all events (arrivals/departures) given the current circumstances and elapses time.
        
        delta_t : float
            The time-step size.
        """
        departures = []
        departing_vehicle_n = self.queue_n.run_event(delta_t=delta_t, saturation_rate=self.traffic_light_ns.saturation_rate(delta_t=delta_t), animate=animate, plt=plt)
        departing_vehicle_w = self.queue_w.run_event(delta_t=delta_t, saturation_rate=self.traffic_light_ew.saturation_rate(delta_t=delta_t), animate=animate, plt=plt)
        departing_vehicle_s = self.queue_s.run_event(delta_t=delta_t, saturation_rate=self.traffic_light_ns.saturation_rate(delta_t=delta_t), animate=animate, plt=plt)
        departing_vehicle_e = self.queue_e.run_event(delta_t=delta_t, saturation_rate=self.traffic_light_ew.saturation_rate(delta_t=delta_t), animate=animate, plt=plt)
        
        if departing_vehicle_n != None:
            departures += [departing_vehicle_n]
            
        if departing_vehicle_w != None:
            departures += [departing_vehicle_w]
            
        if departing_vehicle_s != None:
            departures += [departing_vehicle_s]
            
        if departing_vehicle_e != None:
            departures += [departing_vehicle_e]
        
        
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
        
        return departures
        
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
        self.moving_vehicles = []
        self.time = 0.
        
    def initialize(self, grid_dimensions: (int,int), grid_distance: float):
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
    
    def set_queue_rate_parameters(self, grid_ind: (int,int), avg_departure_time: float, avg_arrival_time_n=np.inf, avg_arrival_time_w=np.inf, avg_arrival_time_s=np.inf, avg_arrival_time_e=np.inf) -> None:
        """
        Sets the departure/arrival rates of the queues within the intersection.
        
        grid_ind : (int,int)
            The grid index of the intersection.
        avg_departure_rate : float
            The average time [s] between departures.
        avg_arrival_time_n : float (optional)
            The average time [s] between arrivals to the northbound queue. Defaults to infinity.
        avg_arrival_time_w : float (optional)
            The average time [s] between arrivals to the westbound queue. Defaults to infinity.
        avg_arrival_time_s : float (optional)
            The average time [s] between arrivals to the southbound queue. Defaults to infinity.
        avg_arrival_time_e : float (optional)
            The average time [s] between arrivals to the eastbound queue. Defaults to infinity.
        """
        self.intersections[grid_ind].initialize_queues(avg_departure_time=avg_departure_time, avg_arrival_time_n=avg_arrival_time_n, avg_arrival_time_w=avg_arrival_time_w, avg_arrival_time_s=avg_arrival_time_s, avg_arrival_time_e=avg_arrival_time_e)
    
    def set_traffic_lights(self, grid_ind: (int,int), traffic_light_ns: TrafficLight.SimpleTrafficLight, traffic_light_ew: TrafficLight.SimpleTrafficLight) -> None:
        """
        Sets the traffic lights of the intersection.
        
        grid_ind : (int,int)
            The grid index of the intersection.
        traffic_light_ns : TrafficLight.SimpleTrafficLight
            The traffic light controlling the north- and southbound queues.
        traffic_light_ew : TrafficLight.SimpleTrafficLight
            The traffic light controlling the east- and westbound queues.
        """
        self.intersections[grid_ind].set_traffic_lights(traffic_light_ns=traffic_light_ns, traffic_light_ew=traffic_light_ew)
        
    def initialize_plot(self, plt):
        fig, ax = plt.subplots()
        ax.axis('equal')
        ax.set(xlim=(-50,(self.grid_dimensions[1]-1)*self.grid_distance+50), ylim=(-(self.grid_dimensions[0]-1)*self.grid_distance-50,50))

        for grid_ind in self.grid_inds:
            center = self.intersections[grid_ind].position
            plt.plot(center[0], center[1], 'x', markersize=8)
        
        return fig, ax
    
    def simulate(self, delta_t: float, end_time: float, animate=False, file_name="simulation.mp4", speed=1) -> None:
        if animate:
            FFMpegWriter = manimation.writers['ffmpeg']
            metadata = dict(title='Simulation', artist='Matplotlib',
                            comment='Visual representation of the simulation.')
            fps = int(speed/delta_t)
            writer = FFMpegWriter(fps=fps, metadata=metadata)

            fig, ax = self.initialize_plot(plt)
            text = plt.gcf().text(0, 0, "Elapsed time: 0s", fontsize=14)

            with writer.saving(fig, file_name, 100):
                while self.time < end_time:
                    self.run_event(delta_t=delta_t, animate=True, plt=plt)
                    text.set_text("Elapsed time: "+str(round(self.time,1))+"s")
                    writer.grab_frame()
        else:
            while self.time < end_time:
                self.run_event(delta_t=delta_t)
        
    def run_event(self, delta_t: float, animate=False, plt=None) -> None:
        """
        Runs all events (departures/arrivals) given the current circumstances and elapses time.
        
        delta_t : float
            The time-step size.
        """
        moving_vehicles = []
        
        for vehicle in self.moving_vehicles: # check if vehicle has arrived to destination
            if vehicle.destination in self.grid_inds and self.distance_to_destination(vehicle=vehicle) <= 1:
                if vehicle.direction == Vehicle.NORTH:
                    self.intersections[vehicle.destination].queue_n.queue_vehicle(arriving_vehicle=vehicle)
                elif vehicle.direction == Vehicle.WEST:
                    self.intersections[vehicle.destination].queue_w.queue_vehicle(arriving_vehicle=vehicle)
                elif vehicle.direction == Vehicle.SOUTH:
                    self.intersections[vehicle.destination].queue_s.queue_vehicle(arriving_vehicle=vehicle)
                elif vehicle.direction == Vehicle.EAST:
                    self.intersections[vehicle.destination].queue_e.queue_vehicle(arriving_vehicle=vehicle)
            else:
                moving_vehicles += [vehicle]
        
        self.moving_vehicles = moving_vehicles
        
        departures = []
        
        for grid_ind in self.grid_inds:
            intersection_departures = self.intersections[grid_ind].run_event(delta_t=delta_t, animate=animate, plt=plt)
            departures += [(departure,grid_ind) for departure in intersection_departures]
            
        self.moving_vehicles += self.update_destinations(departures)
        
        moving_vehicles = []
        
        for vehicle in self.moving_vehicles:
            if animate:
                if vehicle.visual == None:
                    vehicle.initialize_plot(plt)
                vehicle.update_plot()
                
            vehicle.time_step(delta_t=delta_t)
            
            if self.out_of_bounds(vehicle): # check if vehicle has exited the network
                if animate:
                    vehicle.remove_plot()
            else:
                moving_vehicles += [vehicle]
            
        
        self.moving_vehicles = moving_vehicles
        self.time = self.intersections[(0,0)].time
            
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
        if vehicle.direction == Vehicle.NORTH and vehicle.position[1] > self.intersections[(0,0)].queue_s.queue.tail_position[1]:
            return True
        elif vehicle.direction == Vehicle.WEST and vehicle.position[0] < self.intersections[(0,0)].queue_e.queue.tail_position[0]:
            return True
        elif vehicle.direction == Vehicle.SOUTH and vehicle.position[1] < self.intersections[self.grid_inds[-1]].queue_n.queue.tail_position[1]:
            return True
        elif vehicle.direction == Vehicle.EAST and vehicle.position[0] > self.intersections[self.grid_inds[-1]].queue_w.queue.tail_position[0]:
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
            
            if vehicle.position[1] < destination_y:
                passed = -1
        elif vehicle.direction == Vehicle.WEST:
            destination_x = self.intersections[vehicle.destination].queue_w.queue.tail_position[0]
            destination_y = self.intersections[vehicle.destination].queue_w.queue.tail_position[1]
            
            if vehicle.position[0] < destination_x:
                passed = -1
        elif vehicle.direction == Vehicle.SOUTH:
            destination_x = self.intersections[vehicle.destination].queue_s.queue.tail_position[0]
            destination_y = self.intersections[vehicle.destination].queue_s.queue.tail_position[1]
            
            if vehicle.position[1] > destination_y:
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
            stats[grid_ind]["N"] = {}
            stats[grid_ind]["N"]["queue_length"] = n_queue_length
            stats[grid_ind]["N"]["arrivals"] = n_arrivals
            stats[grid_ind]["N"]["departures"] = n_departures
            stats[grid_ind]["N"]["wait_time"] = n_wait_time

            stats[grid_ind]["W"] = {}
            stats[grid_ind]["W"]["queue_length"] = w_queue_length
            stats[grid_ind]["W"]["arrivals"] = w_arrivals
            stats[grid_ind]["W"]["departures"] = w_departures
            stats[grid_ind]["W"]["wait_time"] = w_wait_time
            
            stats[grid_ind]["S"] = {}
            stats[grid_ind]["S"]["queue_length"] = s_queue_length
            stats[grid_ind]["S"]["arrivals"] = s_arrivals
            stats[grid_ind]["S"]["departures"] = s_departures
            stats[grid_ind]["S"]["wait_time"] = s_wait_time

            stats[grid_ind]["E"] = {}
            stats[grid_ind]["E"]["queue_length"] = e_queue_length
            stats[grid_ind]["E"]["arrivals"] = e_arrivals
            stats[grid_ind]["E"]["departures"] = e_departures
            stats[grid_ind]["E"]["wait_time"] = e_wait_time
            
        return stats
    
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
        traffic_light : TrafficLight.SimpleTrafficLight (optional)
            The traffic light controlling the queue.
        """
        fig, axs = plt.subplots(3, figsize=fig_size, dpi=90, sharex=True)
        queue_data = self.get_stats()[grid_ind][direction]
        t = np.arange(start_time,end_time,delta_t)
        
        start_ind = int(start_time/delta_t)
        end_ind = int(end_time/delta_t)
        
        axs[0].plot(t, queue_data['queue_length'][start_ind:end_ind], 'black')
        axs[0].set(ylabel='number of vehicles')
        axs[0].set_title('Queue length')
        axs[0].label_outer()
        
        axs[1].plot(t, queue_data['arrivals'][start_ind:end_ind], 'black')
        axs[1].set(ylabel='number of vehicles')
        axs[1].set_title('Total nbr. of arrivals')
        axs[1].label_outer()
        
        axs[2].plot(t, queue_data['departures'][start_ind:end_ind], 'black')
        axs[2].set(xlabel='time [s]', ylabel='number of vehicles')
        axs[2].set_title('Total nbr. of departures')
        axs[2].label_outer()

        if traffic_light != None:
            traffic_light.plot_green_light(axs[0],end_time)
            traffic_light.plot_green_light(axs[2],end_time)

        return fig, axs