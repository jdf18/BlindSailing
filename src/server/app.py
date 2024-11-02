from os import path
from flask import Flask, abort, jsonify, render_template, request, redirect, send_file, url_for, session

def create_app() -> Flask:
    web_src_path = path.abspath("src/web")
    app = Flask(__name__, 
                template_folder=web_src_path,
                static_folder=web_src_path
                )

    @app.route("/", methods=["GET"])
    def render_html_index():
        return render_template("html/index.html")

    @app.route("/game", methods=["GET"])
    def render_html_game():
        return render_template("html/game.html")
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="localhost", port=5000)