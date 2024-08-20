# imported for 'user authentication' tutorial:
# https://www.youtube.com/watch?v=jAgll-Z5mc8
from flask import Flask
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth

## creating app and its API
app = Flask(__name__)
api = Api(app, prefix="/api/v1")
auth = HTTPBasicAuth() # set up basic authentication

USER_DATA = { # this should be imported from your database
	"admin": "SuperSecretPwd"
}

@auth.verify_password
def verify(username, password):
	if not (username and password):
		return False
	return USER_DATA.get(username)==password

class PrivateR(Resource):
	@auth.login_required # decorator that states login is required
	def get(self):
		return {"meaning of life": 42}

## add resources
api.add_resource(PrivateR, '/private')

if __name__ == '__main__':
	app.run(debug=True) # enable debug mode -> show interactive traceback in the browser when an unhandled error occurs during a request, port=8080 if you want to use a specific port number