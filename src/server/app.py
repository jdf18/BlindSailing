from os import path
from flask import Flask, abort, jsonify, render_template, request, redirect, send_file, url_for, session

from user_manager import UserManager, User, LoginStatus
from game_server import GamesServer, GamesManager



def create_app() -> Flask:
    web_src_path = path.abspath("src/web")
    app = Flask(__name__, 
                template_folder=web_src_path,
                static_folder=web_src_path
                )

    app.secret_key = 'password'

    server = GamesServer()
    
    # Returns a 401 error if the user has not been connected yet
    def require_connection():
        if 'login_status' in session:
            if server.user_manager.users[session.get('login_uid')] == None:
                print("401 sent as users table has None entry")
                abort(401)
                return
            if session.get('login_status') == LoginStatus.CONNECTED.value:
                return
        print("401 sent as no login_status")
        abort(401)

    def force_connection():
        if 'login_status' in session:
            if session.get('login_status') == LoginStatus.CONNECTED.value:
                if server.user_manager.users[session.get('login_uid')] != None:
                    return
        
        session['login_status'] = LoginStatus.UNKNOWN.value
            
        if session.get('login_status') == LoginStatus.UNKNOWN.value:
            uid = server.user_manager.connect()
            if uid == -1:
                return 'Too many concurrent users', 503
            
            session['login_status'] = LoginStatus.CONNECTED.value
            session['login_uid'] = uid
            return 'User connected', 200
        require_connection()

    @app.route("/", methods=["GET"])
    def render_html_index():
        return render_template("html/index.html")

    @app.route("/lobby/<lobby_uid>", methods=["GET"])
    def render_html_game(lobby_uid):
        force_connection()
        user_uid = session['login_uid']
        user: User = server.user_manager.users[user_uid]
        try:
            lobby: GamesManager.Lobby = list(filter(
                lambda x:x.lobby_uid==lobby_uid, 
                server.games_manager.lobby_uids
                ))[0]
        except:
            return "Error, lobby does not exist" # todo: make this actually good lookin
        
        if lobby.lobby_state == GamesManager.Lobby.LobbyState.RUNNING:
            return "Error, lobby is full", 401
        if not user_uid in lobby.players:
            # First time user has entered the lobby
            if not user.current_lobby == lobby_uid:
                # Second player
                lobby.players[1] = user_uid
                user.current_lobby = lobby_uid
                print("2nd player joined", user_uid)

                lobby.lobby_state = GamesManager.Lobby.LobbyState.RUNNING

        else:
            print("1st player joined", user_uid)
            game = server.games_manager.game_servers[lobby.game_index]

        return render_template("html/game.html")


    @app.route("/api/v1/debug", methods=["POST"]) 
    def api_debug():
        print("login_status", session.get('login_status'))
        print("login_uid", session.get('login_uid'))
        print("users", server.user_manager.users)
        return 'ok', 200

    @app.route("/api/v1/connect", methods=["POST"]) 
    def api_connect():
        if not 'login_status' in session:
            session['login_status'] = LoginStatus.UNKNOWN.value

        if session.get('login_status') == LoginStatus.CONNECTED.value:
            if server.user_manager.users[session.get('login_uid')] == None:
                session['login_status'] = LoginStatus.UNKNOWN.value
            else:
                return jsonify('Already connected'), 400 
        
        if session.get('login_status') == LoginStatus.UNKNOWN.value:
            uid = server.user_manager.connect()
            if uid == -1:
                return 'Too many concurrent users', 503
            
            session['login_status'] = LoginStatus.CONNECTED.value
            session['login_uid'] = uid
            return 'User connected', 200

    @app.route("/api/v1/disconnect", methods=["POST"]) 
    def api_disconnect():
        if not 'login_status' in session:
            session['login_status'] = LoginStatus.UNKNOWN.value
        
        if session.get('login_status') == LoginStatus.UNKNOWN.value:
            return 'User is not connected', 400 
        
        elif session.get('login_status') == LoginStatus.CONNECTED.value:
            server.user_manager.disconnect(
                session.get('login_uid')
            )
            session['login_status'] = LoginStatus.UNKNOWN.value
            session['login_uid'] = -1
            return 'User disconnected', 200

    @app.route("/api/v1/create_lobby", methods=["POST"]) 
    def api_create_lobby():
        force_connection()
        user_uid = session['login_uid']
        user: User = server.user_manager.users[user_uid]

        lobby = server.start_lobby()
        print("Starting lobby")
        user.current_lobby = lobby.lobby_uid
        lobby.players[0] = user_uid

        return jsonify({'lobby_uid' : lobby.lobby_uid}), 200

    # @app.route("/api/v1/game", methods=["POST"]) 
    # def api_game():
    #     if not request.is_json:
    #         return 'None', 400
        
    #     data = request.get_json()

    #     return jsonify(data), 200 

    @app.route("/api/v1/game_is_my_turn", methods=["POST"])
    def api_game_is_my_turn():
        require_connection()
        user_uid = session['login_uid']
        user: User = server.user_manager.users[user_uid]
        lobby: GamesManager.Lobby = list(filter(
            lambda x:x.lobby_uid==user.current_lobby, 
            server.games_manager.lobby_uids
            ))[0]
        game = server.games_manager.game_servers[lobby.game_index]
            
        my_turn: bool = False

        # todo

        return jsonify({'is_my_turn': my_turn}), 200 
    
    @app.route("/api/v1/game_fire", methods=["POST"])
    def api_game_fire():
        require_connection()
        user_uid = session['login_uid']
        user: User = server.user_manager.users[user_uid]
        lobby: GamesManager.Lobby = list(filter(
            lambda x:x.lobby_uid==user.current_lobby, 
            server.games_manager.lobby_uids
            ))[0]
        game = server.games_manager.game_servers[lobby.game_index]

        if not request.is_json:
            return 'None', 400
        success: bool = False

        data = request.get_json()
        # data['ship_index']: int
        # data['position']: tuple[int, int]

        # todo

        return jsonify({'success': success}), 200 
    
    @app.route("/api/v1/game_move", methods=["POST"])
    def api_game_move():
        require_connection()
        user_uid = session['login_uid']
        user: User = server.user_manager.users[user_uid]
        lobby: GamesManager.Lobby = list(filter(
            lambda x:x.lobby_uid==user.current_lobby, 
            server.games_manager.lobby_uids
            ))[0]
        game = server.games_manager.game_servers[lobby.game_index]

        if not request.is_json:
            return 'None', 400
        success: bool = False

        data: dict[
            'ship_index': int,
            'count': int
            ] = request.get_json()

        # todo

        return jsonify({'success': success}), 200 
    
    @app.route("/api/v1/game_rotate", methods=["POST"])
    def api_game_rotate():
        require_connection()
        user_uid = session['login_uid']
        user: User = server.user_manager.users[user_uid]
        lobby: GamesManager.Lobby = list(filter(
            lambda x:x.lobby_uid==user.current_lobby, 
            server.games_manager.lobby_uids
            ))[0]
        game = server.games_manager.game_servers[lobby.game_index]

        if not request.is_json:
            return 'None', 400
        success: bool = False

        data: dict[
            'ship_index': int,
            'is_acw': bool
            ] = request.get_json()

        # todo

        return jsonify({'success': success}), 200 
    
    @app.route("/api/v1/game_has_game_finished", methods=["POST"])
    def api_game_has_game_finished():
        require_connection()
        user_uid = session['login_uid']
        user: User = server.user_manager.users[user_uid]
        lobby: GamesManager.Lobby = list(filter(
            lambda x:x.lobby_uid==user.current_lobby, 
            server.games_manager.lobby_uids
            ))[0]
        game = server.games_manager.game_servers[lobby.game_index]

        has_game_finished: bool = False

        # todo

        return jsonify({'has_game_finished': has_game_finished}), 200 
    
    @app.route("/api/v1/game_is_winner", methods=["POST"])
    def api_game_is_winner():
        require_connection()
        user_uid = session['login_uid']
        user: User = server.user_manager.users[user_uid]
        lobby: GamesManager.Lobby = list(filter(
            lambda x:x.lobby_uid==user.current_lobby, 
            server.games_manager.lobby_uids
            ))[0]
        game = server.games_manager.game_servers[lobby.game_index]

        is_player_winner: bool = False

        # todo

        return jsonify({'is_winner': is_player_winner}), 200 
    
    @app.route("/api/v1/game_get_availiable_ships", methods=["POST"])
    def api_game_get_availiable_ships():
        require_connection()
        user_uid = session['login_uid']
        user: User = server.user_manager.users[user_uid]
        lobby: GamesManager.Lobby = list(filter(
            lambda x:x.lobby_uid==user.current_lobby, 
            server.games_manager.lobby_uids
            ))[0]
        game = server.games_manager.game_servers[lobby.game_index]

        availiable_ships: list = []

        # todo

        return jsonify(availiable_ships), 200 
    
    @app.route("/api/v1/graphics_get_grid_size", methods=["POST"])
    def api_graphics_get_grid_size():
        require_connection()
        user_uid = session['login_uid']
        user: User = server.user_manager.users[user_uid]
        lobby: GamesManager.Lobby = list(filter(
            lambda x:x.lobby_uid==user.current_lobby, 
            server.games_manager.lobby_uids
            ))[0]
        game = server.games_manager.game_servers[lobby.game_index]
        
        grid_size: list = []

        # todo

        return jsonify(grid_size), 200 
    
    @app.route("/api/v1/graphics_get_visible_friendly_ships", methods=["POST"])
    def api_get_visible_friendly_ships():
        require_connection()
        user_uid = session['login_uid']
        user: User = server.user_manager.users[user_uid]
        lobby: GamesManager.Lobby = list(filter(
            lambda x:x.lobby_uid==user.current_lobby, 
            server.games_manager.lobby_uids
            ))[0]
        game = server.games_manager.game_servers[lobby.game_index]
        
        visible_friendly_ships: list[dict[
            'filename':str,
            'position':tuple[int, int],
            'facing':int]] = []

        # todo

        return jsonify(visible_friendly_ships), 200 
    
    @app.route("/api/v1/graphics_get_visible_enemy_ships", methods=["POST"])
    def api_get_visible_enemy_ships():
        require_connection()
        user_uid = session['login_uid']
        user: User = server.user_manager.users[user_uid]
        lobby: GamesManager.Lobby = list(filter(
            lambda x:x.lobby_uid==user.current_lobby, 
            server.games_manager.lobby_uids
            ))[0]
        game = server.games_manager.game_servers[lobby.game_index]
        
        visible_enemy_ships: list[dict[
            'filename':str,
            'position':tuple[int, int],
            'facing':int]] = []

        # todo

        return jsonify(visible_enemy_ships), 200 
    
    @app.route("/api/v1/graphics_get_damaged_squares", methods=["POST"])
    def api_get_damaged_squares():
        require_connection()
        user_uid = session['login_uid']
        user: User = server.user_manager.users[user_uid]
        lobby: GamesManager.Lobby = list(filter(
            lambda x:x.lobby_uid==user.current_lobby, 
            server.games_manager.lobby_uids
            ))[0]
        game = server.games_manager.game_servers[lobby.game_index]
        
        damaged_squares: list[tuple[int, int]] = []

        # todo

        return jsonify(damaged_squares), 200 
    
    @app.route("/api/v1/graphics_get_hidden_cells", methods=["POST"])
    def api_get_hidden_cells():
        require_connection()
        user_uid = session['login_uid']
        user: User = server.user_manager.users[user_uid]
        lobby: GamesManager.Lobby = list(filter(
            lambda x:x.lobby_uid==user.current_lobby, 
            server.games_manager.lobby_uids
            ))[0]
        game = server.games_manager.game_servers[lobby.game_index]
        
        hidden_cells: list[tuple[int, int]] = []

        # todo

        return jsonify(hidden_cells), 200 
    
    @app.route("/api/v1/graphics_get_visible_cells", methods=["POST"])
    def api_get_visible_cells():
        require_connection()
        user_uid = session['login_uid']
        user: User = server.user_manager.users[user_uid]
        lobby: GamesManager.Lobby = list(filter(
            lambda x:x.lobby_uid==user.current_lobby, 
            server.games_manager.lobby_uids
            ))[0]
        game = server.games_manager.game_servers[lobby.game_index]
        
        visible_cells: list[tuple[int, int]] = []

        # todo

        return jsonify(visible_cells), 200 
    
    @app.route("/api/v1/graphics_get_possible_attacks", methods=["POST"])
    def api_get_possible_attacks():
        require_connection()
        user_uid = session['login_uid']
        user: User = server.user_manager.users[user_uid]
        lobby: GamesManager.Lobby = list(filter(
            lambda x:x.lobby_uid==user.current_lobby, 
            server.games_manager.lobby_uids
            ))[0]
        game = server.games_manager.game_servers[lobby.game_index]
        
        possible_attacks: list[tuple[int, int]] = []

        if not request.is_json:
            return 'None', 400
        success: bool = False

        data: dict[
            'ship_index': int
            ] = request.get_json()

        # todo

        return jsonify(possible_attacks), 200 


    
    return app
    


    
    return app




if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="localhost", port=5000)