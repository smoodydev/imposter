from flask import Flask, render_template, request, session, redirect, url_for
import os

import random
from flask_pymongo import PyMongo

if os.path.exists("env.py"):
    import env

app = Flask(__name__)
app.config["MONGO_DBNAME"] = "pokemomCards"

app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "")
app.secret_key = 'your_secret_key'

mongo = PyMongo(app)
all_games = {}



@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    session['username'] = username
    return redirect(url_for('index')) 


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index')) 

@app.route('/creategame', methods=['POST'])
def creategame():
    gamename = request.form['gamename']
    session['gamename'] = gamename
    session['admin'] = True
    all_games[gamename] = {"words":[], "imposter": "", "word":"", "players": [session["username"]]}
    return redirect(url_for('index')) 


@app.route('/joingame', methods=['POST'])
def joingame():
    if "username" in session:
        gamename = request.form['gamename']
        if gamename in all_games:
            if session["username"] not in all_games[gamename]["players"]:
                session['gamename'] = gamename
                session['admin'] = False
                all_games[gamename]["players"].append(session["username"])
    return redirect(url_for('index')) 


@app.route('/start')
def start():
    if "admin" in session:
        global all_games
        game = all_games[session['gamename']]
        
        if len(game["players"]) > 1 and len(game["words"]) >= 1:
            word = random.choice(game["words"])
            possible = game["players"].copy()
            possible.remove(word["author"])
            game["imposter"] = random.choice(possible)
            game["word"] = word
            game["words"] = [d for d in game["words"] if d.get('word') != word['word']]

    return redirect(url_for('index')) 



@app.route('/', methods=['GET', 'POST'])
def index():
    if "gamename" in session:
        global all_games
        word_list = all_games[session["gamename"]]
    else:
        word_list = []


    if request.method == 'POST':

        if "gamename" not in session:
            return redirect(url_for('index'))
        
        word = request.form['word']
        mongo.db.words.insert_one({"word": word})
        all_games[session['gamename']]["words"].append({"author": session["username"], "word": word})

    return render_template('index.html', word_list=word_list)


if __name__ == '__main__':
    app.run(host=os.environ.get('IP', "0.0.0.0"),
            port=int(os.environ.get('PORT', 5000)),
            debug=False)