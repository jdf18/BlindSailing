from typing import Optional
from enum import Enum

class LoginStatus(Enum):
    UNKNOWN = 0
    CONNECTED = 1

class User:
    def __init__(self):
        pass

class UserManager:
    def __init__(self, max_users: int = 64):
        self.max_concurrent_users: int = max_users
        self.current_users: int = 0

        self.users: list[Optional[User]] = [None for _ in range(max_users)]

    def find_unused_uid(self) -> int:
        if self.current_users >= self.max_concurrent_users:
            return -1
        
        for i, e in enumerate(self.users):
            if e == None:
                return i
            
    def connect(self) -> int:
        if self.current_users < self.max_concurrent_users:
            new_uid = self.find_unused_uid()
            self.users[new_uid] = User()
            self.current_users += 1
            return new_uid
        return -1

    def disconnect(self, user_id: int):
        if self.users[user_id] != None:
            self.users[user_id] = None
            self.current_users -= 1
            return True
        return False