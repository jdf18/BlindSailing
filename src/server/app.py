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
        print(server.games_manager.lobby_uids)
        lobby: GamesManager.Lobby = list(filter(
            lambda x:x.lobby_uid==lobby_uid, 
            server.games_manager.lobby_uids
            ))[0]
        
        if not user_uid in lobby.whitelist:
            # First tiem user has entered the lobby
            if not user.current_lobby == lobby_uid:
                # Second player
                lobby.whitelist[1] = user_uid
                user.current_lobby = lobby_uid
                print("2nd player joined", user_uid)

        else:
            print("1st player joined", user_uid)
            game = server.games_manager.game_servers[lobby.game_index]

        return render_template("html/game.html")


    @app.route("/api/v1/debug", methods=["POST"]) 
    def api_debug():
        print(session.get('login_status'))
        print(session.get('login_uid'))
        print(server.user_manager.users)
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
        lobby.whitelist[0] = user_uid

        return jsonify({'lobby_uid' : lobby.lobby_uid}), 200

    @app.route("/api/v1/game", methods=["POST"]) 
    def api_game():
        if not request.is_json:
            return 'None', 400
        
        data = request.get_json()

        return jsonify(data), 200 
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="localhost", port=5000)