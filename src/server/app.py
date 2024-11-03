from os import path
from flask import Flask, abort, jsonify, render_template, request, redirect, send_file, url_for, session, send_from_directory
import numpy as np
from user_manager import UserManager, User, LoginStatus
from game_server import GamesServer, GamesManager



def create_app() -> Flask:
    assets_src_path = path.abspath("src/assets")
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
                game = server.games_manager.game_servers[lobby.game_index]
                game.start(user_uid)

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

        lobby = server.start_lobby(user_uid)
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
            
        my_turn: bool = game.isPlayerTurn(user_uid)

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

        try:
            game.shootFromShip(game.getShipIndex(user_uid, data['ship_index']), np.asarray(data['position']))
            success = True
            game.logMove(game.getShipIndex(user_uid, data['ship_index']))
            game.changeTurnifFinished()
        except ValueError:
            pass
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

        try:
            game.moveShip(game.getShipIndex(user_uid, data['ship_index']), data['count'])
            success = True
            game.logMove(game.getShipIndex(user_uid, data['ship_index']))
            game.changeTurnifFinished()
        except ValueError:
            pass
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

        try:
            if data['is_acw']:
                game.rotateShip(game.getShipIndex(user_uid, data['ship_index']), 3)
            else:
                game.rotateShip(game.getShipIndex(user_uid, data['ship_index']), 1)
            success = True
            game.logMove(game.getShipIndex(user_uid, data['ship_index']))
            game.changeTurnifFinished()
        except ValueError:
            pass

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

        has_game_finished: bool = game.hasFinished

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

        is_player_winner: bool = game.hasWon(user_uid)

        return jsonify({'is_winner': is_player_winner}), 200 
    
    @app.route("/api/v1/game_get_available_ships", methods=["POST"])
    def api_game_get_available_ships():
        require_connection()
        user_uid = session['login_uid']
        user: User = server.user_manager.users[user_uid]
        lobby: GamesManager.Lobby = list(filter(
            lambda x:x.lobby_uid==user.current_lobby, 
            server.games_manager.lobby_uids
            ))[0]
        game = server.games_manager.game_servers[lobby.game_index]

        available_ships: list = game.getUnmovedShips(user_uid)
        for i in range(len(available_ships)):
            available_ships[i] = game.getPlayerIndex(available_ships[i], user_uid)
        return jsonify(available_ships), 200 
    
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
        
        grid_size: list = [int(game.getGridSize()[0]), int(game.getGridSize()[1])]
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
        
        visible_friendly_ships: list[tuple[
            str,
            tuple[int, int],
            int]] = []
        visibleList = game.getVisibleFriendlyShips(user_uid)
        for ind in visibleList:
            pos = game.board.ships[ind].getTopLeft()
            toAdd = (
                game.playerShipDict[game.board.ships[ind].id],
                (int(pos[0]), int(pos[1])),
                game.board.ships[ind].getFacingasValue()
            )
            visible_friendly_ships.append(toAdd)
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
        
        visible_enemy_ships: list[tuple[
            str,
            tuple[int, int],
            int]] = []

        for ind in game.getAllVisibleEnemyShips(user_uid):
            pos = game.board.ships[ind].getTopLeft()
            toAdd = (
                game.enemyShipDict[game.board.ships[ind].id],
                (int(pos[0]), int(pos[1])),
                game.board.ships[ind].getFacingasValue()
            )
            visible_enemy_ships.append(toAdd)
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

        for ind in game.getVisibleFriendlyShips(user_uid):
            damagedCoords = game.board.ships[ind].getDamagedCoords()
            for coords in damagedCoords:
                damaged_squares.append((coords[0], coords[1]))
        visibleTiles = game.getAllVisibleTiles(user_uid)
        for ind in game.getAllVisibleEnemyShips(user_uid):
            damagedCoords = [coords for coords in game.board.ships[ind].getDamagedCoords() if coords in visibleTiles]
            for coords in damagedCoords:
                damaged_squares.append((int(coords[0]), int(coords[1])))

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

        hiddenCells = game.getAllHiddenTiles(user_uid)
        for cell in hiddenCells:
            hidden_cells.append((int(cell[0]), int(cell[1])))

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

        visibleCells = game.getAllVisibleTiles(user_uid)
        for cell in visibleCells:
            visible_cells.append((int(cell[0]), int(cell[1])))

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
        
        firableTiles = game.getFirableTiles(game.getShipIndex(user_uid, data['ship_index']))
        for item in firableTiles:
            possible_attacks.append((item[0], item[1]))

        return jsonify(possible_attacks), 200 
    
    @app.route("/api/v1/api_is_player_one", methods=["POST"])
    def api_is_player_one():
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

        return jsonify({'is_player_one':game.isPlayerOne(user_uid)}), 200 
    
    @app.route("/api/v1/api_get_ship_data", methods=["POST"])
    def api_get_ship_data():
        require_connection()
        user_uid = session['login_uid']
        user: User = server.user_manager.users[user_uid]
        lobby: GamesManager.Lobby = list(filter(
            lambda x:x.lobby_uid==user.current_lobby, 
            server.games_manager.lobby_uids
            ))[0]
        game = server.games_manager.game_servers[lobby.game_index]
        
        ship_data: dict["filename":str, "is_dead":bool] = request.get_json()

        shipData = game.getShipData(game.getShipIndex(user_uid, ship_data['ship_index']), user_uid)

        return jsonify(shipData), 200 
    
    @app.route('/api/v1/end_turn', methods=['POST'])
    def api_t():
        require_connection()

        user_uid = session['login_uid']
        user: User = server.user_manager.users[user_uid]
        lobby: GamesManager.Lobby = list(filter(
            lambda x:x.lobby_uid==user.current_lobby, 
            server.games_manager.lobby_uids
            ))[0]
        game = server.games_manager.game_servers[lobby.game_index]

        game.startTurn(user_uid)

        return 'None', 200
        
    

    @app.route("/assets/<path:filename>")
    def download_asset(filename):
        return send_from_directory(assets_src_path, filename, as_attachment=False)


    
    return app
    




if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="localhost", port=5000)