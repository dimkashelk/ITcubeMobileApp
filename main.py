from datetime import datetime
from hashlib import sha256
from flask import Flask, jsonify, request
from session import Session
import random

app = Flask(__name__)

session = Session()


def get_token(login):
    return sha256(random.randbytes(256) + login.encode("utf-8")).hexdigest()


def get_hash_password(password):
    return sha256(password.encode('utf-8')).hexdigest()


@app.route("/")
@app.route("/api/documentation", methods=["GET"])
def docs():
    return jsonify({"description": "This small docs for RESTapi server",
                    "/api": "This main method to check connection",
                    "/api/authorization": {"methods": ["GET"],
                                           "description": "method for get authorization token",
                                           "params": {
                                               "login": "string",
                                               "password": "string"
                                           }},
                    "/api/refresh": {"methods": ["GET"],
                                     "description": "method for refresh authorization token every 10 minutes (!!!)",
                                     "params": {
                                         "login": "string",
                                         "password": "string",
                                         "old_token": "string"
                                     }},
                    "/api/add_user": {"methods": ["POST"],
                                      "description": "method for add user",
                                      "params": {
                                          "login": "string",
                                          "password": "string"
                                      }}}), 200


@app.route("/api", methods=["GET"])
def main():
    return jsonify({"status": "ok"}), 200


@app.route('/api/authorization', methods=['GET'])
def get_authorize_token():
    data = request.json
    user = session.get_user_by_login(data['login'])
    if user is None:
        return jsonify({"status": "user not found"}), 404
    if user.token != '':
        return jsonify({"status": "Error. Please use /api/refresh to refresh your token"}), 400
    if get_hash_password(data['password']) == user.password:
        time = datetime.utcnow().isoformat()
        token = get_token(user.login)
        session.set_token(data['login'], token, time)
    else:
        return jsonify({"status": "wrong password"}), 400
    return jsonify({"status": "ok",
                    "token": user.token}), 200


@app.route("/api/refresh", methods=["GET"])
def refresh():
    data = request.json
    user = session.get_user_by_login(data['login'])
    if user is None:
        return jsonify({"status": "user not found"}), 404
    if user.token != data["old_token"]:
        return jsonify({"status": "uncorrected old token"})
    if get_hash_password(data['password']) != user.password:
        return jsonify({"status": "uncorrected password"})
    time = datetime.utcnow().isoformat()
    token = get_token(user.login)
    session.set_token(user.login, token, time)
    return jsonify({"status": "ok",
                    "token": token})


@app.route("/api/add_user", methods=["POST"])
def add_user():
    data = request.json
    user = session.get_user_by_login(data['login'])
    if user is not None:
        return jsonify({"status": "login in database, please use another login"})
    session.add_new_user(data['login'], get_hash_password(data['password']))
    token = get_token(data['login'])
    time = datetime.utcnow().isoformat()
    session.set_token(data['login'], token, time)
    return jsonify({"status": "ok",
                    "token": token})


@app.errorhandler(500)
def error_500(e):
    return jsonify({"status": "server error, please check your request"}), 500


if __name__ == '__main__':
    app.run(port=5000)
