import numpy as np
import ships
ROT90 = np.array([[0, -1], [1, 0]])
class Board:
    def __init__(self, gridSize: np.array, ships: list):
        self.gridSize = gridSize
        self.ships = ships
        self.grid = [[None for i in range(gridSize[0])] for i in range(gridSize[1])]
        for i in range(len(ships)):
            for coord in ships[i].getCoords():
                self.grid[coord[0]][coord[1]] = i
    
    def addShip(self, ship: ships.ship) -> int:
        self.ships.append(ship)
        return len(ships) - 1

    def indexGrid(self, x: int, y: int) -> int:
        return self.grid[x][y]
    
    def indexGrid(self, pos: np.array) -> int:
        return self.grid[pos[0]][pos[1]]

    def moveShip(self, index: int, dist: int):
        shipFacing = self.ships[index].facing
        coords = self.ships[index].getCoords()
        for i in range(len(coords)):
            coord = coords[i] + shipFacing * dist
            if coord[0] >= self.gridSize[0] or coord[1] >= self.gridSize[1]:
                raise ValueError("Cannot move a ship beyond the bounds of the board")
            val = self.indexGrid(coord)
            if val != None and val != index:
                raise ValueError("Cannot move ship into a position which contains another ship.")
        self.ships[index].step(dist)
        for i in range(len(coords)):
            self.grid[coords[i][0]][coords[i][1]] = None
        for coord in self.ships[index].getCoords():
            self.grid[coord[0]][coord[1]] = index
    
    def rotateShip(self, index: int, times: int):
        shipCentre = self.ships[index].getCentre()
        coords = self.ships[index].getCoords()
        for i in range(times):
            for x in range(len(coords)):
                coords[x] = np.matmul(rot90, (coords[x] - shipCentre)) + shipCentre
        for coord in coords:
            if coord[0] >= self.gridSize[0] or coord[1] >= self.gridSize[1]:
                raise ValueError("Cannot rotate this ship as it would be over the edge of the board.")
        for coord in coords:
            val = self.indexGrid(coord)
            if val != None and val != index:
                raise ValueError("Cannot rotate this ship as it would be overlapping another ship.")
        for coord in self.ships[index].getCoords():
            self.grid[coord[0]][coord[1]] = None
        self.ships[index].rotate(times)
        for coord in coords:
            self.grid[coord[0]][coord[1]] = index
        



