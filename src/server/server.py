from user_manager import UserManager, User


class Server:
    user_manager: UserManager

    def __init__(self, max_game_servers: int = 64):
        self.user_manager = UserManager()

