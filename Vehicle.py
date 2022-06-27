NORTH = (0,-1)
WEST = (-1,0)
SOUTH = (0,1)
EAST = (1,0)

class Vehicle:
    def __init__(self):
        self.position = (0,0) # upper left corner
        self.direction = (0,0) # 4 possible directions
        self.destination = None
        self.full_speed = 0.
        self.speed = 0. # [m/s]
        self.length = 0.
        self.wait_time = 0.
        self.time = 0.
        
    def initialize(self, position: (float, float), direction: (int, int), full_speed=14, length=5):
        self.position = position
        self.direction = direction
        self.full_speed = full_speed
        self.speed = full_speed
        self.length = length
        
    def time_step(self, delta_t: float):
        x = self.position[0]
        x_dir = self.direction[0]
        y = self.position[1]
        y_dir = self.direction[1]
        self.position = (x+x_dir*self.speed*delta_t, y+y_dir*self.speed*delta_t)
        self.time += delta_t
        
        if self.speed <= 0:
            self.wait_time += delta_t
            
    def right_turn(self):
        if self.direction == NORTH:
            self.direction = EAST
        elif self.direction == WEST:
            self.direction = NORTH
        elif self.direction == SOUTH:
            self.direction = WEST
        elif self.direction == EAST:
            self.direction = SOUTH
    
    def left_turn(self):
        if self.direction == NORTH:
            self.direction = WEST
        elif self.direction == WEST:
            self.direction = SOUTH
        elif self.direction == SOUTH:
            self.direction = EAST
        elif self.direction == EAST:
            self.direction = NORTH
            
    def stop(self) -> None:
        self.speed = 0
            
    def accelerate(self) -> None:
        self.wait_time = 0.
        self.speed = self.full_speed