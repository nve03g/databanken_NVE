from flask import Flask, jsonify
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth
import sqlite3 as sql

## creating app and its API
app = Flask(__name__)
api = Api(app, prefix="/api/v1")
auth = HTTPBasicAuth() # set up basic authentication
# user authentication tutorial: https://www.youtube.com/watch?v=jAgll-Z5mc8
# possible authentication modes:
# HTTPBasicAuth, HTTPDigestAuth, HTTPTokenAuth

# database handling
dbName = "my_database.db"
### --------------------------------------------REMOVE THIS----------------------------------------------- ###
USER_DATA = { # this should be imported from your database
	"admin": "adminPW",
	"user": "userPW"
}
EVENT_DATA = {
	0: ["name0", "date0", "time0", "location0", "host0", "poster0", "category0", "sale0", "artists0"],
	1: ["name1", "date1", "time1", "location1", "host1", "poster1", "category1", "sale1", "artists1"],
	2: ["name2", "date2", "time2", "location2", "host2", "poster2", "category2", "sale2", "artists2"]
}
### ------------------------------------------------------------------------------------------------------ ###

# maybe predefine queries here?

@auth.verify_password
def verify(username, password):
	if not (username and password):
		return False
	return USER_DATA.get(username)==password

# zorgen dat er geen critical gegevens via postman gegeven worden, dat kan hacker dan ook doen, doe zoveel mogelijk in code zelf (queries) => security ligt op de server
"""
user role bepalen bij verify_password, als gevonden in host table dan set role to host
"""
# user role dependence: https://flask-httpauth.readthedocs.io/en/latest/
# @auth.login_required(role='admin')
# def admin_only(self):
# 	return "Hello {}, you are an admin!".format(auth.current_user())

class PrivateR(Resource):
	@auth.login_required # decorator that states login is required, to protect this resources' get() from unauthorized users
	def get(self):
		return {"meaning of life": 42}
	
    
## add resources
api.add_resource(PrivateR, '/private')
# api.add_resource(EventsR, '/events')
# api.add_resource(EventR, '/events/<int:eventID>')


if __name__ == '__main__':
	app.run(debug=True) # enable debug mode -> show interactive traceback in the browser when an unhandled error occurs during a request, port=8080 if you want to use a specific port number