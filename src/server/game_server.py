import random
from enum import Enum

from user_manager import UserManager, User

class Game:
    pass

class GamesManager:
    class LobbyInfo:
        class LobbyState(Enum):
            OPEN = 0
            RUNNING = 1
            GENERATED = 2
        
        lobby_state: LobbyState
        lobby_uid: str
        game_index: int
        whitelist: list[int]

        def __init__(self, state, uid, game_index) -> None:
            self.lobby_state = state
            self.lobby_uid = uid
            self.game_index = game_index

    game_servers: list[Game]
    lobby_uids: list[LobbyInfo]

    def __init__(self, max_game_servers: int = 64):
        self.game_servers = [None for _ in range(max_game_servers)]

    def generate_lobby_uid(self):
        uid: str = ''
        
        while True:
            uid = str(random.randint(100000, 999999))

            for e in self.lobby_uids:
                if e.lobby_uid == uid: continue
            break

        self.lobby_uids.append(
            self.LobbyInfo(
                self.LobbyInfo.LobbyState.GENERATED, 
                uid,
                None
            )
        )

        return uid

class GamesServer:
    user_manager: UserManager

    games_manager: GamesManager

    def __init__(self, max_game_servers: int = 64):
        self.user_manager = UserManager()
        self.games_manager = GamesManager()

    def start_lobby(self) -> GamesManager.LobbyInfo:
        lobby_uid = self.games_manager.generate_lobby_uid()
        game = Game() # todo 

        for i in range(len(self.games_manager.game_servers)):
            if self.games_manager.game_servers[i] == None:
                game_index = i
                self.games_manager.game_servers[i] = game
                break
        else:
            raise BufferError("Games servers array full")

        lobby: GamesManager.LobbyInfo = filter(lambda x:x.lobby_uid == lobby_uid, self.games_manager.lobby_uids)[0]
        lobby.lobby_state = GamesManager.LobbyInfo.LobbyState.OPEN
        lobby.lobby_uid = lobby_uid
        lobby.game_index = game_index

        return lobby



