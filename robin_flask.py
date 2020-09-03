#!/usr/bin/env python

import flask
from flask_cors import CORS, cross_origin
import robinsquad
app = flask.Flask(__name__) # a Flask object
app.secret_key = 'gNMsBGT8xPxJkUl2VeODQnFf6bSUuxZcV;pN$m6!vE<]d*;' #session
CORS(app)


@app.route('/home', methods = ['POST', 'GET'])
def home():
    
    # retrieve creds and log into Robinhood 
    email = flask.request.form.get("email")
    password = flask.request.form.get("password")
    success = robinsquad.login(email, password)

    # bad creds, redirect to welcome
    if not success:
        err = {
            "msg": "Bad credentials"
        }
        return flask.jsonify(err) 
    
    err = {
        "msg": "Signed in"
    }
    return flask.jsonify(err) 

@app.route('/account', methods=['GET'])
def account():
    # return account info
    email = flask.request.args.get("email")
    data = robinsquad.get_acc_info(email)
    return flask.jsonify(data)
     

@app.route('/invest', methods=['GET'])
def invest():
    # display new purchases for user
    email = flask.request.args.get("email")
    password = flask.request.args.get("password")
    max_amt = int(flask.request.args.get("max_amt"))
    purchases = robinsquad.rebalance(email, password, max_amt)
    return flask.jsonify(purchases)

@app.route('/logout')
def logout():
    # clear session for next user
    email = flask.request.args.get("email")
    robinsquad.logout(email)
    err = {
        "msg": "Success logout"
    }
    return flask.jsonify(err)

if __name__ == "__main__":
    app.run(debug=True, port=5000)