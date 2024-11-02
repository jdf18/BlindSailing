import numpy as np
# Base class for all ships. front is the co-ords of the front of the ship, facing is the direction the ship is facing
# Length is the length of the ship (all ships have width 1). viewRadius and fireRadius are the radiuses the ship can see and shoot in
class ship:
    def __init__(self, length: int, front: np.array, facing: np.array, viewRadius: int, fireRadius: int):
        self.length = length
        self.front = front
        self.facing = facing
        self.viewRadius = viewRadius
        self.fireRadius = fireRadius
        self.rot90 = np.array([[0, -1], [1, 0]])

    def step(self, distance: int):
        self.front += distance * self.facing
    
    def rotate(self, times: int):
        centre = self.front - (self.facing * (self.length // 2))
        print(centre)
        for i in range(times):
            self.front = np.matmul(self.rot90, (self.front - centre)) + centre
        self.facing = np.matmul(self.rot90, self.facing)


# 5-long
class airCarrier(ship):
    def __init__(self, front, facing):
        super().__init__(5, front, facing, 12, 6)

# 4-long
def Battleship(ship):
    def __init__(self, front, facing):
        super().__init__(4, front, facing, 8, 8)

# 3-long
def Cruiser(ship):
    def __init__(self, front, facing):
        super().__init__(3, front, facing, 6, 6)

# 3-long
def Submarine(ship):
    def __init__(self, front, facing):
        super().__init__(3, front, facing, 5, 12)

# 2-long
def Destroyer(ship):
    def __init__(self, front, facing):
        super().__init__(2, front, facing, 4, 4)
