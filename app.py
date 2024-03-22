from flask import Flask, render_template, request, session, redirect, url_for
import os

import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'
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
        word = (random.choice(game["words"]))
        possible = game["players"].copy()
        possible.remove(word["author"])
        game["imposter"] = random.choice(possible)
        game["word"] = word
        
 

    return redirect(url_for('index')) 



@app.route('/', methods=['GET', 'POST'])
def index():
    global all_games

    if request.method == 'POST':
        word = request.form['word']
        # all_games[session['gamename']] = []

        all_games[session['gamename']]["words"].append({"author": session["username"], "word": word})

    return render_template('index.html', word_list=all_games)


if __name__ == '__main__':
    app.run(host=os.environ.get('IP', "0.0.0.0"),
            port=int(os.environ.get('PORT', 5000)),
            debug=False)