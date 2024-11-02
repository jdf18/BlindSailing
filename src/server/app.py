from os import path
from flask import Flask, abort, jsonify, render_template, request, redirect, send_file, url_for, session

from user_manager import UserManager, User, LoginStatus



def create_app() -> Flask:
    web_src_path = path.abspath("src/web")
    app = Flask(__name__, 
                template_folder=web_src_path,
                static_folder=web_src_path
                )
    
    user_manager = UserManager()

    @app.route("/", methods=["GET"])
    def render_html_index():
        return render_template("html/index.html")

    @app.route("/game", methods=["GET"])
    def render_html_game():
        return render_template("html/game.html")

    @app.route("/api/v1/connect", methods=["POST"]) 
    def api():
        if not 'login_status' in session:
            session['login_status'] = LoginStatus.UNKNOWN
        
        if session.get('login_status') == LoginStatus.UNKNOWN:
            uid = user_manager.connect()
            if uid == -1:
                return 'Too many concurrent users', 503
            
            session['login_status'] = LoginStatus.CONNECTED
            session['login_uid'] = uid
            return 'User connected', 200
        
        elif session.get('login_status') == LoginStatus.CONNECTED:
            return 'Already connected', 400 

    @app.route("/api/v1/disconnect", methods=["POST"]) 
    def api():
        if not 'login_status' in session:
            session['login_status'] = LoginStatus.UNKNOWN
        
        if session.get('login_status') == LoginStatus.UNKNOWN:
            return 'User is not connected', 400 
        
        elif session.get('login_status') == LoginStatus.CONNECTED:
            user_manager.disconnect(
                session.get('login_uid')
            )
            return 'User disconnected', 400

    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="localhost", port=5000)