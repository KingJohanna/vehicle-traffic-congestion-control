import numpy as np
import random
import Vehicle
import math

class TrafficLight:
    def __init__(self):
        self.visuals = [None, None]
        self.service = False
        self.service_history = [self.service]
        self.positions = [(0,0), (0,0)]
        self.time = 0
        self.adaptive = False
        self.num_cycles = [0]
        self.switches = [0]
        
    def time_step(self, delta_t: float) -> None:
        """
        Elapses time by one time-step
        """
        self.time += delta_t
        self.service = self.saturation_rate()
        self.service_history += [self.service]
        
        self.num_cycles += [self.num_cycles[-1]]
        
        switch = self.service - self.service_history[-2]
        self.switches += [switch]
        
        if switch < 0:
            self.num_cycles[-1] += 1
        
    def red_to_green_stats(self):
        switches = [service-prev_service for service,prev_service in zip(self.service_history+[0],[0]+self.service_history)][:-2]
        
        res = [0]
        for switch in switches:
            if switch > 0:
                res += [(res[-1]+switch)]
            else:
                res += [res[-1]]
            
        return res[1:], switches
        
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
        self.num_cycles = [0]
        self.switches = [0]
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
        self.num_cycles = [0]
        self.switches = [0]
        
    def initialize(self, traffic_light: TrafficLight) -> None:
        """
        Initializes the TrafficLightMirror instance.
        
        traffic_light : TrafficLight
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
        self.num_cycles = [0]
        self.switches = [0]
        
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
        self.num_cycles = [0]
        self.switches = [0]
        
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
    global EMPTY, EMPTY_OTHER, EMPTY_MIDWAY, EMPTY_OTHER_MIDWAY, WAIT
    
    EMPTY = 0
    EMPTY_OTHER = 1
    EMPTY_MIDWAY = 2
    EMPTY_OTHER_MIDWAY = 3
    WAIT = 4
    
    def __init__(self):
        self.visuals = [None, None]
        self.service = False
        self.service_history = [self.service]
        self.positions = [(0,0), (0,0)]
        self.sensor_position = (0,0)
        self.time = 0
        self.adaptive = True
        self.objective_length = 0
        self.case = WAIT
        self.num_cycles = [0]
        self.switches = [0]
        self.sensor_depth = 0
        self.rule = 0
        self.range = 50
        
    def initialize(self, sensor_depth: int, rule=1):
        self.sensor_depth = sensor_depth
        self.rule = rule
        
    def distance_to_sensor(self, position: (float, float)):
        return math.hypot(position[0]-self.sensor_position[0], position[1]-self.sensor_position[1])
    
    def sense(self, queue_1, queue_2, opposite_queue_1, opposite_queue_2) -> None:
        queue_1 = list(filter(lambda vehicle: self.distance_to_sensor(position=vehicle.position) < self.range, queue_1))
        queue_2 = list(filter(lambda vehicle: self.distance_to_sensor(position=vehicle.position) < self.range, queue_2))
        opposite_queue_1 = list(filter(lambda vehicle: self.distance_to_sensor(position=vehicle.position) < self.range, opposite_queue_1))
        opposite_queue_2 = list(filter(lambda vehicle: self.distance_to_sensor(position=vehicle.position) < self.range, opposite_queue_2))
        queue_1.sort(key=lambda vehicle: self.distance_to_sensor(position=vehicle.position))
        queue_2.sort(key=lambda vehicle: self.distance_to_sensor(position=vehicle.position))
        opposite_queue_1.sort(key=lambda vehicle: self.distance_to_sensor(position=vehicle.position))
        opposite_queue_2.sort(key=lambda vehicle: self.distance_to_sensor(position=vehicle.position))
        
        vehicles = []
        opposite_vehicles = []
        
        if len(queue_1) > self.sensor_depth:
            vehicles += queue_1[:self.sensor_depth]
        else:
            vehicles += queue_1
            
        if len(queue_2) > self.sensor_depth:
            vehicles += queue_2[:self.sensor_depth]
        else:
            vehicles += queue_2
            
        if len(opposite_queue_1) > self.sensor_depth:
            opposite_vehicles += opposite_queue_1[:self.sensor_depth]
        else:
            opposite_vehicles += opposite_queue_1
            
        if len(opposite_queue_2) > self.sensor_depth:
            opposite_vehicles += opposite_queue_2[:self.sensor_depth]
        else:
            opposite_vehicles += opposite_queue_2
           
        vehicles = list(filter(lambda vehicle: self.distance_to_sensor(position=vehicle.position) < self.range, vehicles))
        opposite_vehicles = list(filter(lambda vehicle: self.distance_to_sensor(position=vehicle.position) < self.range, opposite_vehicles))
        
        if self.rule == 1:
            queue_length = len(vehicles)
            opposite_queue_length = len(opposite_vehicles)
            
            if self.case == EMPTY_MIDWAY:
                if queue_length <= self.objective_length:
                    self.case = EMPTY_OTHER
            elif self.case == EMPTY_OTHER_MIDWAY:
                if opposite_queue_length <= self.objective_length:
                    self.case = EMPTY

            if self.case == EMPTY:
                if queue_length <= 0:
                    self.case = WAIT
            elif self.case == EMPTY_OTHER:
                if opposite_queue_length <= 0:
                    self.case = WAIT

            if self.case == WAIT:
                if queue_length >= 1 and opposite_queue_length < 2*self.sensor_depth:
                    if opposite_queue_length <= 0:
                        self.case = EMPTY
                    elif opposite_queue_length == queue_length:
                        self.case = EMPTY
                    elif opposite_queue_length > queue_length:
                        if opposite_queue_length-queue_length > 2:
                            self.case = EMPTY_OTHER_MIDWAY
                            self.objective_length = opposite_queue_length-queue_length
                        else:
                            self.case = EMPTY_OTHER
                elif queue_length == 1 and opposite_queue_length >= 2*self.sensor_depth:
                    self.case = EMPTY

                if opposite_queue_length >= 1 and queue_length < 2*self.sensor_depth:
                    if queue_length <= 0:
                        self.case = EMPTY_OTHER
                    elif queue_length > opposite_queue_length:
                        if queue_length-opposite_queue_length > 2:
                            self.case = EMPTY_MIDWAY
                            self.objective_length = queue_length-opposite_queue_length
                        else:
                            self.case = EMPTY
                elif opposite_queue_length == 1 and queue_length >= 2*self.sensor_depth:
                    self.case = EMPTY_OTHER
                                
        elif self.rule == 2:
            platoons = []
            if len(vehicles) > 0:
                platoons = [[vehicles[0]]]
            platoon_metrics = []
            opposite_platoons = []
            if len(opposite_vehicles) > 0:
                opposite_platoons = [[opposite_vehicles[0]]]
            opposite_platoon_metrics = []
            
            for i in range(1, len(vehicles)): #split into platoons
                if (vehicles[i].direction == Vehicle.NORTH and vehicles[i-1].tail_position[1]-vehicles[i].position[1] <= vehicles[i].length) or (vehicles[i].direction == Vehicle.EAST and vehicles[i-1].tail_position[0]-vehicles[i].position[0] <= vehicles[i].length) or (vehicles[i].direction == Vehicle.SOUTH and vehicles[i].position[1]-vehicles[i-1].tail_position[1] <= vehicles[i].length) or (vehicles[i].direction == Vehicle.WEST and vehicles[i].position[0]-vehicles[i-1].tail_position[0] <= vehicles[i].length):
                    platoons[-1] += [vehicles[i]]
                else:
                    platoons += [[vehicles[i]]]
              
            for platoon in platoons:
                platoon_metrics += [(len(platoon), sum([vehicle.wait_time for vehicle in platoon])/len(platoon))]
            
            for i in range(1, len(opposite_vehicles)):
                if (opposite_vehicles[i].direction == Vehicle.NORTH and opposite_vehicles[i-1].tail_position[1]-opposite_vehicles[i].position[1] <= opposite_vehicles[i].length) or (opposite_vehicles[i].direction == Vehicle.EAST and opposite_vehicles[i-1].tail_position[0]-opposite_vehicles[i].position[0] <= opposite_vehicles[i].length) or (opposite_vehicles[i].direction == Vehicle.SOUTH and opposite_vehicles[i].position[1]-opposite_vehicles[i-1].tail_position[1] <= opposite_vehicles[i].length) or (opposite_vehicles[i].direction == Vehicle.WEST and opposite_vehicles[i].position[0]-opposite_vehicles[i-1].tail_position[0] <= opposite_vehicles[i].length):
                    opposite_platoons[-1] += [opposite_vehicles[i]]
                else:
                    opposite_platoons += [[opposite_vehicles[i]]]
                    
            for platoon in opposite_platoons:
                opposite_platoon_metrics += [(len(platoon), sum([vehicle.wait_time for vehicle in platoon])/len(platoon))]
                
            #print(self.time, platoon_metrics, opposite_platoon_metrics)
            
            if self.case == EMPTY_MIDWAY:
                if len(platoons) <= self.objective_length:
                    self.case = WAIT
            elif self.case == EMPTY_OTHER_MIDWAY:
                if len(opposite_platoons) <= self.objective_length:
                    self.case = WAIT
            elif self.case == EMPTY:
                if len(platoons) <= 0:
                    self.case = WAIT
            elif self.case == EMPTY_OTHER:
                if len(opposite_platoons) <= 0:
                    self.case = WAIT
                    
            if self.case == WAIT:
                if len(opposite_platoons) <= 0:
                    self.case = EMPTY
                    
                elif len(platoons) <= 0:
                    self.case = EMPTY_OTHER

                elif len(platoons) == 1 and len(opposite_platoons) == 1:
                    distance = self.distance_to_sensor(position=vehicles[-1].position)
                    speed = vehicles[-1].full_speed
                    
                    opposite_distance = self.distance_to_sensor(position=vehicles[-1].position)
                    opposite_speed = opposite_vehicles[0].full_speed
                    
                    cum_metric = platoon_metrics[0][1] + opposite_distance/opposite_speed
                    opposite_cum_metric = opposite_platoon_metrics[0][1] + distance/speed
                    
                    if cum_metric >= opposite_cum_metric:
                        self.case = EMPTY
                    else:
                        self.case = EMPTY_OTHER
                        
                elif len(platoons) > 1 and len(opposite_platoons) > 1:
                    distance = self.distance_to_sensor(position=platoons[0][-1].position)
                    speed = platoons[0][-1].full_speed
                    
                    opposite_distance = self.distance_to_sensor(position=platoons[0][-1].position)
                    opposite_speed = opposite_platoons[0][0].full_speed

                    cum_metric = opposite_distance/opposite_speed + sum([metric[1] for metric in platoon_metrics])
                    cum_metric /= len(platoons)
                    opposite_cum_metric = distance/speed + sum([metric[1] for metric in opposite_platoon_metrics])
                    opposite_cum_metric /= len(opposite_platoons)

                    if cum_metric >= opposite_cum_metric:
                        self.case = EMPTY_MIDWAY
                        self.objective_length = len(platoons)-1
                    else:
                        self.case = EMPTY_OTHER_MIDWAY
                        self.objective_length = len(opposite_platoons)-1
                    
        self.update_service()
        
    def update_service(self):
        if self.case in [EMPTY, EMPTY_MIDWAY]:
            self.service = 1
        elif self.case in [EMPTY_OTHER, EMPTY_OTHER_MIDWAY]:
            self.service = 0
    
    def saturation_rate(self, delta_t=0.):
        return self.service