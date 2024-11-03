import numpy as np
import ships
import math

ROT90 = np.array([[0, -1], [1, 0]])

#Main class storing the board state, includes lots of methods
class Board:
    def __init__(self, gridSize: np.array):
        self.gridSize = gridSize
        self.ships: list[ships.Ship] = []
        self.grid = [[None for i in range(gridSize[0])] for i in range(gridSize[1])]
    
    def addShip(self, ship: ships.Ship) -> int:
        for coord in ship.getCoords():
            if self.indexGrid(coord) != None:
                raise ValueError("Cannot place a ship in an occupied position")
            if (coord[0] >= self.gridSize[0] or coord[1] >= self.gridSize[1]) or (coord[0] < 0 or coord[1] < 0):
                raise ValueError("Cannot place ship out of bounds")
        self.ships.append(ship)
        for coord in ship.getCoords():
            self.updateGrid(coord, len(self.ships) - 1)
        return len(self.ships) - 1

    def indexGrid(self, x: int, y: int) -> int:
        return self.grid[x][y]
    
    def indexGrid(self, pos: np.array) -> int:
        return self.grid[pos[0]][pos[1]]
    
    def updateGrid(self, pos: np.array, val: int):
        self.grid[pos[0]][pos[1]] = val

    def canMoveShip(self, index: int, dist: int) -> bool:
        if self.ships[index].isDead():
            return False
        shipFacing = self.ships[index].facing
        coords = self.ships[index].getCoords()
        for i in range(len(coords)):
            coord = coords[i] + shipFacing * dist
            if coord[0] >= self.gridSize[0] or coord[1] >= self.gridSize[1] or coord[0] < 0 or coord[1] < 0:
                return False
            val = self.indexGrid(coord)
            if val != None and val != index:
                return False
        return True

    def moveShip(self, index: int, dist: int):
        if not self.canMoveShip:
            raise ValueError("Cannot make that move.")
        coords = self.ships[index].getCoords()
        self.ships[index].step(dist)
        for i in range(len(coords)):
            self.updateGrid(coords[1], None)
        for coord in self.ships[index].getCoords():
            self.updateGrid(coord, index)
    
    def canRotateShip(self, index: int, times: int) -> bool:
        if self.ships[index].isDead():
            return False
        shipCentre = self.ships[index].getCentre()
        coords = self.ships[index].getCoords()
        for i in range(times):
            for x in range(len(coords)):
                coords[x] = np.matmul(ROT90, (coords[x] - shipCentre)) + shipCentre
        for coord in coords:
            if coord[0] >= self.gridSize[0] or coord[1] >= self.gridSize[1] or coord[0] < 0 or coord[1] < 0:
                return False
        for coord in coords:
            val = self.indexGrid(coord)
            if val != None and val != index:
                return False
        return True
    
    def rotateShip(self, index: int, times: int):
        if not self.canRotateShip(index, times):
            raise ValueError("Cannot rotate ship.")
        coords = self.ships[index].getCoords()
        for coord in coords:
            self.updateGrid(coord, None)
        self.ships[index].rotate(times)
        for coord in coords:
            self.updateGrid(coord, index)
        
    def shoot(self, coord):
        ind = self.indexGrid(coord)
        if ind != None:
            ships[ind].hit(coord)
            if ships[ind].isDead():
                for c in ships[ind].getCoords():
                    self.updateGrid(c, None)
            return (True, ind, ships[ind].isDead())
        return (False, None, None)
    
    def shootFromShip(self, index: int, coord: np.array):
        ship = self.ships[index]
        radius = ship.fireRadius
        centre = ship.getCentre()
        if self.getDist(centre, coord) <= radius:
            return self.shoot(coord)
        raise ValueError("This ship cannot shoot that far.")
    
    def getDist(self, coord1: np.array, coord2: np.array) -> float:
        diff = coord2 - coord1
        return math.sqrt(diff[0] ** 2 + diff[1] ** 2)
    
    def getFirableTiles(self, index: int) -> list[np.array]:
        ship = self.ships[index]
        centre = ship.getCentre()
        firableTiles = []
        for y in range(self.gridSize[1]):
            for x in range(self.gridSize[0]):
                arr = np.array([x, y])
                if self.getDist(arr, centre) <= ship.fireRadius:
                    firableTiles.append(arr)
        return firableTiles

    def getVisibleTiles(self, index: int) -> tuple[list[np.array], list[np.array]]:
        ship = self.ships[index]
        centre = ship.getCentre()
        visibleTiles = []
        invisibleTiles = []
        for y in range(self.gridSize[1]):
            for x in range(self.gridSize[0]):
                arr = np.array([x, y])
                if self.getDist(arr, centre) <= ship.viewRadius:
                    visibleTiles.append(tuple(arr))
                else:
                    invisibleTiles.append(tuple(arr))
        return visibleTiles, invisibleTiles

    def getVisibleEnemyShips(self, index: int) -> list[int]:
        ship = self.ships[index]
        centre = ship.getCentre()
        visible = []
        for i in range(len(self.ships)):
            if ship.team == self.ships[i].team:
                continue
            coords = self.ships[i].getCoords()
            for coord in coords:
                if self.getDist(coord, centre) <= ship.viewRadius:
                    visible.append(i)
                    break
        return visible
    

    
    def getVisibleFriendlyShips(self, team: int) -> list[int]:
        visible = []
        for i in range(len(self.ships)):
            if self.ships[i].team == team and not self.ships[i].isDead():
                visible.append(i)
        return visible
    
    def getInvisibleEnemyShips(self, index: int) -> list[int]:
        ship = self.ships[index]
        centre = ship.getCentre()
        invisible = []
        for i in range(len(self.ships)):
            if ship.team == self.ships[i].team:
                continue
            coords = self.ships[i].getCoords()
            for coord in coords:
                if self.getDist(coord, centre) > ship.viewRadius:
                    invisible.append(i)
                    break
        return invisible


    def getVisibleTilesTuple(self, index: int) -> tuple[tuple[tuple[int, int]], tuple[tuple[int, int]]]:
        visibleTiles, invisibleTiles = self.getVisibleTiles(index)
        return (tuple(tile) for tile in visibleTiles), (tuple(tile) for tile in invisibleTiles)


class Game:
    def __init__(self, p1ID: int):
        self.board = Board(np.array([50, 30]))
        self.p1Ships = []
        self.p2Ships = []
        self.p1Ships.append(self.board.addShip(ships.AirCarrier(np.array([1, 8]), np.array([1, 0]), p1ID)))
        self.p1Ships.append(self.board.addShip(ships.Battleship(np.array([1, 6]), np.array([1, 0]), p1ID)))
        self.p1Ships.append(self.board.addShip(ships.Cruiser(np.array([1, 4]), np.array([1, 0]), p1ID)))
        self.p1Ships.append(self.board.addShip(ships.Submarine(np.array([1, 2]), np.array([1, 0]), p1ID)))
        self.p1Ships.append(self.board.addShip(ships.Destroyer(np.array([1, 0]), np.array([1, 0]), p1ID)))
        self.p2Ships.append(self.board.addShip(ships.AirCarrier(np.array([10, 8]), np.array([-1, 0]), None)))
        self.p2Ships.append(self.board.addShip(ships.Battleship(np.array([10, 6]), np.array([-1, 0]), None)))
        self.p2Ships.append(self.board.addShip(ships.Cruiser(np.array([10, 4]), np.array([-1, 0]), None)))
        self.p2Ships.append(self.board.addShip(ships.Submarine(np.array([10, 2]), np.array([-1, 0]), None)))
        self.p2Ships.append(self.board.addShip(ships.Destroyer(np.array([10, 0]), np.array([-1, 0]), None)))
        self.turn = p1ID
        self.players = [p1ID, None]
        self.movedShips = []
        self.playerShipDict = {
            "AirCarrier": "airCarrier-0.png",
            "Battleship": "battleship-0.png",
            "Cruiser": "cruiser-0.png",
            "Submarine": "submarine-0.png",
            "Destroyer": "destroyer-0.png"
        }
        self.enemyShipDict = {
            "AirCarrier": "airCarrier-1.png",
            "Battleship": "battleship-1.png",
            "Cruiser": "cruiser-1.png",
            "Submarine": "submarine-1.png",
            "Destroyer": "destroyer-1.png"
        }

    def start(self, p2ID):
        self.players[1] = p2ID
        for ind in self.p2Ships:
            self.board.ships[ind].team = p2ID
    
    def logMove(self, index: int):
        self.movedShips.append(index)
    
    def startTurn(self, playerID):
        self.turn = playerID
        self.movedShips = []

    def changeTurnifFinished(self):
        if self.turn == self.players[0]:
            no_of_alive_ships = len(filter(lambda x: not x.isDead(), (self.board.ships[x] for x in self.p1Ships)))
            if not len(self.movedShips) == len(self.p1Ships):
                return
            self.startTurn(self.players[1])
        if self.turn == self.players[1]:
            no_of_alive_ships = len(filter(lambda x: not x.isDead(), (self.board.ships[x] for x in self.p2Ships)))
            if not len(self.movedShips) == len(self.p2Ships):
                return
            self.startTurn(self.players[0])


    def getUnmovedShips(self, playerID):
        if playerID == self.players[0]:
            return [ind for ind in self.p1Ships if ind not in self.movedShips]
        elif playerID == self.players[1]:
            return [ind for ind in self.p2Ships if ind not in self.movedShips]
    
    def getPlayerIndex(self, shipIndex, playerID):
        if playerID == self.player[0]:
            return self.p1Ships.index(shipIndex)
        if playerID == self.player[1]:
            return self.p2Ships.index(shipIndex)
    def addShip(self, ship: ships.Ship) -> int:
        return self.board.addShip(ship)
    def moveShip(self, index: int, dist: int):
        self.board.moveShip(index, dist)
    def rotateShip(self, index: int, times: int):
        self.board.rotateShip(index, times)
    def shoot(self, coord):
        return self.board.shoot(coord)
    def shootFromShip(self, index: int, coord: np.array):
        return self.board.shootFromShip(index, coord)
    def getVisibleTiles(self, index: int) -> tuple[list[np.array], list[np.array]]:
        return self.board.getVisibleTiles(index)
    def getVisibleEnemyShips(self, index: int) -> list[int]:
        return self.board.getVisibleEnemyShips(index)
    def getVisibleFriendlyShips(self, team: int) -> list[int]:
        return self.board.getVisibleFriendlyShips(team)
    def getVisibleTilesTuple(self, index: int) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
        return self.board.getVisibleTilesTuple(index)
    
    def hasWon(self, team):
        if team == self.players[0]:
            for ship in self.p2Ships:
                if not ship.isDead():
                    return False
        elif team == self.players[1]:
            for ship in self.p1Ships:
                if not ship.isDead():
                    return False
        return True
    
    def getGridSize(self):
        return self.board.gridSize
    
    def getPlayerTurn(self):
        return self.turn
    
    def isPlayerTurn(self, playerID):
        return playerID == self.turn
    
    def getShipIndex(self, playerID, playerIndex):
        if playerID == self.players[0]:
            return self.p1Ships[playerIndex]
        elif playerID == self.player[1]:
            return self.p2Ships[playerIndex]
        raise ValueError("Invalid player ID")
    
    def hasFinished(self):
        return self.hasWon(self.players[0]) or self.hasWon(self.players[1])
    
    def getAllVisibleEnemyShips(self, playerID: int) -> set:
        if playerID == self.players[0]:
            totalSet = set()
            for ind in self.p1Ships:
                totalSet |= set(tuple(self.getVisibleEnemyShips(ind)))
            return totalSet
        if playerID == self.players[1]:
            totalSet = set()
            for ind in self.p2Ships:
                totalSet |= set(tuple(self.getVisibleEnemyShips(ind)))
            return totalSet
        raise ValueError("PlayerID does not correspond to a player.")
    
    def getAllVisibleTiles(self, playerID: int) -> set:
        allTiles = set()
        if playerID == self.players[0]:
            for ind in self.p1Ships:
                allTiles |= set(self.getVisibleTilesTuple(ind)[0])
            return allTiles
        if playerID == self.players[1]:
            for ind in self.p2Ships:
                allTiles |= set(self.getVisibleTilesTuple(ind)[0])
            return allTiles
        raise ValueError("PlayerID does not correspond to a player.")
    
    def getAllHiddenTiles(self, playerID: int) -> set:
        if playerID == self.players[0]:
            if len(self.p1Ships) == 0:
                return set()
            allTiles = set(self.getVisibleTilesTuple(self.p1Ships[0])[1])
            for ind in self.p1Ships[1:]:
                allTiles &= set(self.getVisibleTilesTuple(ind)[1])
            return allTiles
        if playerID == self.players[1]:
            if len(self.p2Ships) == 0:
                return set()
            allTiles = set(self.getVisibleTilesTuple(self.p2Ships[0])[1])
            for ind in self.p2Ships[1:]:
                allTiles &= set(self.getVisibleTilesTuple(ind)[1])
            return allTiles
        raise ValueError("PlayerID does not correspond to a player.")
    
    def getFirableTiles(self, index: int) -> list[np.array]:
        return self.board.getFirableTiles(index)
    
