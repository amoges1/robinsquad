#!/usr/bin/env python

import flask
import robinsquad
app = flask.Flask(__name__) # a Flask object
app.secret_key = 'gNMsBGT8xPxJkUl2VeODQnFf6bSUuxZcV;pN$m6!vE<]d*;' #session

@app.route('/')
def welcome():
    # redirect based on session
    if 'email' in flask.session:
        return flask.redirect(flask.url_for("home"))    
    return flask.render_template('welcome.html')

@app.route('/home', methods = ['POST', 'GET'])
def home():
    # return/update Robinhood account in session
    if 'email' in flask.session:
        email, password = flask.session['email'], flask.session['password']
        robinsquad.get_acc_info(email, password)
        return flask.render_template('home.html', email=email)

     # no session, redirect to welcome
    if flask.request.method == 'GET':
        # note: url_for params: function, not url
        return flask.redirect(flask.url_for("welcome")) 
    
    # retrieve creds and log into Robinhood 
    email = flask.request.form.get('email')
    password = flask.request.form.get('password')
    success =  robinsquad.get_acc_info(email, password)

    # bad creds, redirect to welcome
    if not success:
        return flask.redirect(flask.url_for("welcome"))
    
    # set session for sucessful login
    flask.session['email'] = email
    flask.session['password'] = password
    
    return flask.render_template('home.html', email=email)

@app.route('/account', methods=['GET'])
def account():
    # return account info
    response = flask.send_file('acc.json')
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/invest', methods=['GET'])
def invest():
    # display new purchases for user
    purchases, email = robinsquad.rebalance()
    return flask.render_template('results.html', purchases = purchases, email = email)

@app.route('/logout')
def logout():
    # clear session for next user
    flask.session.clear()
    return flask.redirect(flask.url_for("welcome"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)