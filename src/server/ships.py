import numpy as np
# Base class for all ships. front is the co-ords of the front of the ship, facing is the direction the ship is facing
# Length is the length of the ship (all ships have width 1). viewRadius and fireRadius are the radiuses the ship can see and shoot in
class ship:
    def __init__(self, length: int, front: np.array, facing: np.array, viewRadius: int, fireRadius: int, team: int):
        self.length = length
        self.front = front
        self.facing = facing
        self.viewRadius = viewRadius
        self.fireRadius = fireRadius
        self.rot90 = np.array([[0, -1], [1, 0]])
        if team != 1 and team != 2:
            raise ValueError("team must be 1 or 2")

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
    def __init__(self, front: np.array, facing: np.array, team: int):
        super().__init__(5, front, facing, 12, 6, team)

# 4-long
class Battleship(ship):
    def __init__(self, front: np.array, facing: np.array, team: int):
        super().__init__(4, front, facing, 8, 8, team)

# 3-long
class Cruiser(ship):
    def __init__(self, front: np.array, facing: np.array, team: int):
        super().__init__(3, front, facing, 6, 6, team)

# 3-long
class Submarine(ship):
    def __init__(self, front: np.array, facing: np.array, team: int):
        super().__init__(3, front, facing, 5, 12, team)

# 2-long
class Destroyer(ship):
    def __init__(self, front: np.array, facing: np.array, team: int):
        super().__init__(2, front, facing, 4, 4, team)
