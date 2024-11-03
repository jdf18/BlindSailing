import numpy as np
# Base class for all ships. front is the co-ords of the front of the ship, facing is the direction the ship is facing
# Length is the length of the ship (all ships have width 1). viewRadius and fireRadius are the radiuses the ship can see and shoot in
class Ship:
    def __init__(self, length: int, front: np.array, facing: np.array, viewRadius: int, fireRadius: int, team: int, id: str):
        self.length = length
        self.front = front
        self.facing = facing
        self.viewRadius = viewRadius
        self.fireRadius = fireRadius
        self.rot90 = np.array([[0, -1], [1, 0]])
        if team != 1 and team != 2:
            raise ValueError("team must be 1 or 2")
        self.team = team
        self.hitSections = [False for i in range(length)]
        self.id = id

    def step(self, distance: int):
        self.front += distance * self.facing
    
    def getCentre(self):
        return self.front - (self.facing * (self.length // 2))
    
    def rotate(self, times: int):
        centre = self.getCentre()
        for i in range(times):
            self.front = np.matmul(self.rot90, (self.front - centre)) + centre
        self.facing = np.matmul(self.rot90, self.facing)
    
    def getCoords(self) -> np.array:
        coords = []
        for i in range(self.length):
            coords.append(self.front - self.facing * i)
        return coords
    
    def hit(self, coord: np.array):
        coords = self.getCoords()
        for i in range(len(coords)):
            if coords[i] == coord:
                self.hitSections[i] == True
    
    def isDead(self) -> bool:
        return all(self.hitSections)
    
    def getFacingasValue(self):
        match self.facing:
            case np.array([-1, 0]):
                return 0
            case np.array([0, -1]):
                return 1
            case np.array([1, 0]):
                return 2
            case np.array([0, 1]):
                return 3
        
    def getDamagedCoords(self):
        coords = self.getCoords()
        return [coords[i] for i in range(len(coords)) if self.hitSections[i]]


# 5-long
class AirCarrier(Ship):
    def __init__(self, front: np.array, facing: np.array, team: int):
        super().__init__(5, front, facing, 12, 6, team, "AirCarrier")

# 4-long
class Battleship(Ship):
    def __init__(self, front: np.array, facing: np.array, team: int):
        super().__init__(4, front, facing, 8, 8, team, "Battleship")

# 3-long
class Cruiser(Ship):
    def __init__(self, front: np.array, facing: np.array, team: int):
        super().__init__(3, front, facing, 6, 6, team, "Cruiser")

# 3-long
class Submarine(Ship):
    def __init__(self, front: np.array, facing: np.array, team: int):
        super().__init__(3, front, facing, 5, 12, team, "Submarine")

# 2-long
class Destroyer(Ship):
    def __init__(self, front: np.array, facing: np.array, team: int):
        super().__init__(2, front, facing, 4, 4, team, "Destroyer")
