#!/usr/bin/env python

import flask
import robinsquad

app = flask.Flask(__name__) # a Flask object

@app.route('/')
def welcome():
    return flask.render_template('welcome.html')

@app.route('/home', methods = ['POST', 'GET'])
def home():

    # No creds, redirect to home
    if flask.request.method == "GET":
        return flask.redirect(flask.url_for("/"))
    
    # Retrieve credentials and log into Robinhood 
    email = flask.request.form.get('email')
    password = flask.request.form.get('password')

    # log into Robinhood
    success =  robinsquad.get_user_info(email, password)

    # Bad creds, redirect to welcome
    if not success:
        return flask.redirect(flask.url_for("/"))
    
    return flask.render_template('home.html', email=email)

@app.route('/account', methods=['GET'])
def account():
    response = flask.send_file('acc.json')
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response 

@app.route('/invest', methods=['GET'])
def invest():

    purchases, email = robinsquad.rebalance()

    return flask.render_template('results.html', purchases = purchases, email = email)
    

if __name__ == "__main__":
    app.run(debug=True, port=5000)