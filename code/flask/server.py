import flask
from flask import Flask, request, jsonify, redirect, render_template
from flask_restful import Resource, Api
import sqlite3 as sql
from flask import session


"""
steps to take in this project:
1 - DONE - make ER diagram
2 - DONE - create my own database (DB browser for SQLite)
3 - learn how to make structured and working code based on my database
4 - make a complete backend (server.py) with all necessary queries
5 - make frontend (client.py) to communicate with backend
6 - learn html to work with frontend
7 - look for additional functionalities
8 - update/rework code
"""



## creating app and its API
app = Flask(__name__)
app.secret_key = "mySecretKey123"  # stel een geheime sleutel in voor sessiebeveiliging
api = Api(app)

## connection to database
## !! open and close the connection as close to the actual database operations as possible !!
dbName = "my_database_V0.db"

## definition of classes

# resource for displaying all events or a specific event, possibility to filter based on category
class EventsR(Resource):
	def get(self, category=None, eventID=None):
		if eventID: # display specific event
			my_query = """SELECT Event.name, Event.date, Event.time, Location.address, Location.city, Location.country, Event.artists, User.firstName, User.lastName, Event.posterURL, Ticket.price, Event.remainingTickets
					  FROM Event
					  INNER JOIN Location ON Event.locationID = Location.locationID
					  INNER JOIN Host ON Event.hostID = Host.hostID
					  INNER JOIN User ON Host.userID = User.userID
					  INNER JOIN Ticket ON Event.eventID = Ticket.eventID
					  WHERE Event.eventID = ?
					  """
			with sql.connect(dbName, check_same_thread=False) as conn:
				response = conn.execute(my_query, (eventID,)).fetchone() # FETCH ONE
			if response: # dus als er een event is met dit eventID
				result = {
					"Name": response[0],
					"Date": response[1],
					"Time": response[2],
					"Location": response[3] + " " + response[4] + " " + response[5],
					"Artist": response[6],
					"Host": response[7] + " " + response[8],
					"Link to poster": response[9],
					"Ticket price": response[10],
					"Tickets remaining": response[11]
				}
				return jsonify(result)
			else:
				return {"Not Found": "Event not found"}, 404
		else:
			if category: # display events based on category
				my_query = """SELECT DISTINCT Event.name, Event.date, Event.time, Location.address, Location.city, Location.country, Event.artists, User.firstName, User.lastName, Event.posterURL, Ticket.price, Event.remainingTickets
							FROM Event
							INNER JOIN Location ON Event.locationID = Location.locationID
							INNER JOIN Host ON Event.hostID = Host.hostID
							INNER JOIN User ON Host.userID = User.userID
							INNER JOIN Ticket ON Event.eventID = Ticket.eventID
							WHERE Event.category = ?
							""" 
							# still make sure only UPCOMING events are shown, preferrably in chronological order, 
							# something like this:
							# WHERE Event.date > strftime('%s', 'now') -- Filters for upcoming events
							# ORDER BY Event.date ASC, Event.time ASC
				with sql.connect(dbName, check_same_thread=False) as conn:
					response = conn.execute(my_query,(category,)).fetchall() # response type: list			
			else: # display all events
				my_query = """SELECT DISTINCT Event.name, Event.date, Event.time, Location.address, Location.city, Location.country, Event.artists, User.firstName, User.lastName, Event.posterURL, Ticket.price, Event.remainingTickets
							FROM Event
							INNER JOIN Location ON Event.locationID = Location.locationID
							INNER JOIN Host ON Event.hostID = Host.hostID
							INNER JOIN User ON Host.userID = User.userID
							INNER JOIN Ticket ON Event.eventID = Ticket.eventID
							""" 
							# still make sure only UPCOMING events are shown, preferrably in chronological order, 
							# something like this:
							# WHERE Event.date > strftime('%s', 'now') -- Filters for upcoming events
							# ORDER BY Event.date ASC, Event.time ASC
				with sql.connect(dbName, check_same_thread=False) as conn:
					response = conn.execute(my_query).fetchall() # response type: list
			result = [
				{
					"Name": element[0],
					"Date": element[1],
					"Time": element[2],
					"Location": element[3] + " " + element[4] + " " + element[5],
					"Artist": element[6],
					"Host": element[7] + " " + element[8],
					"Link to poster": element[9],
					"Ticket price": element[10],
					"Tickets remaining": element[11]
				}
				for element in response
			]
			return jsonify({"events": result})
	
	
# # display all UPCOMING events	-----------> UNDER CONSTRUCTION, first fix date format
"""
class UpcomingEventsR(Resource):
	def get(self):
		my_query = SELECT DISTINCT Event.name, Event.date, Event.time, Location.address, Location.city, Location.country, Event.artists, User.firstName, User.lastName, Event.posterURL, Ticket.price, Event.remainingTickets
					  FROM Event
					  INNER JOIN Location ON Event.locationID = Location.locationID
					  INNER JOIN Host ON Event.hostID = Host.hostID
					  INNER JOIN User ON Host.userID = User.userID
					  INNER JOIN Ticket ON Event.eventID = Ticket.eventID
					  WHERE Event.date
					  
					  # still make sure only UPCOMING events are shown, preferrably in chronological order, 
					  # something like this:
					  # WHERE Event.date > strftime('%s', 'now') -- Filters for upcoming events
					  # ORDER BY Event.date ASC, Event.time ASC
		with sql.connect(dbName, check_same_thread=False) as conn:
			response = conn.execute(my_query).fetchall() # response type: list
		result = [
			{
                "Name": element[0],
                "Date": element[1],
                "Time": element[2],
                "Location": element[3] + " " + element[4] + " " + element[5],
                "Artist": element[6],
                "Host": element[7] + " " + element[8],
                "Link to poster": element[9],
                "Ticket price": element[10],
                "Tickets remaining": element[11]
            }
			for element in response
		]
		return jsonify({"events": result})
"""


# register a new user
class RegisterR(Resource):
	def post(self):
		# collect new incoming user data
		username = request.json.get("username")
		password = request.json.get("password")
		email = request.json.get("email")
		firstName = request.json.get("firstName")
		lastName = request.json.get("lastName")
		userType = request.json.get("userType") # provide dropdown menu in HTML code

		# check whether user already exists
		conn = sql.connect(dbName, check_same_thread=False)
		my_query = """SELECT * FROM User WHERE username=?"""
		response = conn.execute(my_query, (username,)).fetchone() # als response == 0 is het een nieuwe user die wilt registreren
		if response:
			return {"Bad Request": "Username already taken"}, 400
		
		# insert new user
		cursor = conn.cursor()
		cursor.execute("INSERT INTO User (username, password, email, firstName, lastName, userType) VALUES (?, ?, ?, ?, ?, ?)", (username, password, email, firstName, lastName, userType))
		conn.commit()
		conn.close()

		# return success message
		return {"Created": "User registered successfully"}, 201
	
# login an existing user
class LoginR(Resource):
	def post(self): # this is a POST method because we're entering (posting) user login data to check whether they can log in or not, although we're not adding new data to the database
		# collect login data
		username = request.json.get('username')
		password = request.json.get('password')

        # check whether user inputs are valid
		my_query = """SELECT * FROM User WHERE username=? AND password=?"""
		with sql.connect(dbName, check_same_thread=False) as conn:
			response = conn.execute(my_query, (username, password)).fetchone() # als response != 0 bestaat deze user
		if response:
			# save username in current session
			session['username'] = username
			return {"OK": "Login successful"}, 200
		
		# trying to log in with a non-existing user
		return {"Unauthorized": "Invalid login data"}, 401

# resource om gebruiker uit te loggen
class LogoutR(Resource):
	def post(self):
        # controleer of gebruiker is ingelogd
		if 'username' in session:
			session.pop('username', None)
			return {"OK": "Logout successful"}, 200
		else:
			return {"Bad Request": "No user is currently logged in"}, 400

# resource to get all users or a specific user
class UsersR(Resource):
	def get(self, userID=None):
		if userID:
			my_query = """SELECT * FROM User WHERE userID = ?"""
			with sql.connect(dbName, check_same_thread=False) as conn:
				response = conn.execute(my_query, (userID,)).fetchone()
			if response: # dus user bestaat
				result = {
					"userID": response[0],
					"username": response[1],
					"password": response[2],
					"email": response[3],
					"user type": response[4],
					"first name": response[5],
					"last name": response[6]
				}
				return jsonify(result)
			else:
				return {"Not Found": "User not found"}, 404
		else:
			my_query = """SELECT * FROM User""" 
			with sql.connect(dbName, check_same_thread=False) as conn:
				response = conn.execute(my_query).fetchall()
			result = [
				{
					"userID": element[0],
					"username": element[1],
					"password": element[2],
					"email": element[3],
					"user type": element[4],
					"first name": element[5],
					"last name": element[6]
				}
				for element in response
			]
			return jsonify({"users": result})


# resource to see or update user's shopping cart (still need to implement DELETE?)
class ShoppingCartR(Resource):
	def get(self, userID):
		# controleer of gebruiker is ingelogd
		if 'username' not in session:
			return {"Unauthorized": "Please log in to view your shopping cart"}, 401
		
		# check if given userID exists
		my_query = """SELECT * FROM User WHERE userID = ?"""
		with sql.connect(dbName, check_same_thread=False) as conn:
			response = conn.execute(my_query, (userID,)).fetchone()
		if response: # dus user bestaat
			# then check whether shopping cart is empty or not
			my_query = """SELECT CartItem.quantity, Ticket.tier, Ticket.price, Event.name
						FROM CartItem
						INNER JOIN Ticket ON CartItem.ticketID = Ticket.ticketID
						INNER JOIN Event ON Ticket.eventID = Event.eventID
						INNER JOIN ShoppingCart ON CartItem.cartID = ShoppingCart.cartID
						WHERE ShoppingCart.userID = ?"""
			with sql.connect(dbName, check_same_thread=False) as conn:
				response = conn.execute(my_query, (userID,)).fetchall() # neem de hele shopping cart
			if response: # dus geen lege shopping cart
				result = [
                    {
                        "Quantity": element[0],
                        "Ticket Tier": element[1],
                        "Ticket Price": element[2],
                        "Event Name": element[3]
                    }
                    for element in response]
				# return jsonify(response)
				return jsonify({"cart":result})
			else:
				return {"Not Found": "Shopping cart is empty"}, 404
		else:
			return {"Not Found": "User not found"}, 404
	
	def post(self, userID): # users can add tickets to their shopping cart
		# collect input cart data
		eventName = request.json.get("eventName") # provide dropdown menu in HTML code
		ticketTier = request.json.get("ticketTier") # provide dropdown menu in HTML code
		quantity = int(request.json.get("quantity"))

		# check validity of input data
		if not (eventName and ticketTier and quantity): # dus niet alle velden ingevuld
			return {"Bad Request": "Missing required data"}, 400
		
		# check if user's shopping cart already exists
		conn = sql.connect(dbName, check_same_thread=False)
		cursor = conn.cursor()
		my_query = """SELECT cartID FROM ShoppingCart WHERE userID = ?"""
		response = cursor.execute(my_query, (userID, )).fetchone() # als response != 0 heeft user al een shopping cart

		# als user nog geen shopping cart heeft, maak er een aan
		# if response == 0:
		if response is None: 
			my_query = """INSERT INTO ShoppingCart (userID) VALUES (?)"""
			cursor.execute(my_query, (userID, ))
			conn.commit()
			cartID = cursor.lastrowid # get cartID of the new cart
		else:
			cartID = response[0] # user already has a shopping cart

		# get ticketID based on eventName and ticketTier
		my_query = """SELECT Ticket.ticketID FROM Ticket
                      INNER JOIN Event ON Ticket.eventID = Event.eventID
                      WHERE Event.name = ? AND Ticket.tier = ?"""
		ticket = cursor.execute(my_query, (eventName, ticketTier)).fetchone()

		if not ticket:  # if the ticket does not exist
			conn.close()
			return {"Bad Request": "Invalid event name or ticket tier"}, 400

		ticketID = ticket[0]

        # insert the new cart item
		cursor.execute("""INSERT INTO CartItem (cartID, ticketID, quantity) VALUES (?, ?, ?)""", (cartID, ticketID, quantity))
		conn.commit()
		conn.close()

        # return success message
		return {"Created": "Ticket added to shopping cart"}, 201
		

# resource to get all events for a specific host
class HostEventsR(Resource):
    def get(self, hostID):
        my_query = """
            SELECT Event.eventID, Event.name, Event.date, Event.time, Location.address, Location.city, Location.country, 
                   COUNT(Ticket.ticketID) AS ticketsSold
            FROM Event
            INNER JOIN Location ON Event.locationID = Location.locationID
            LEFT JOIN Ticket ON Event.eventID = Ticket.eventID
            WHERE Event.hostID = ?
            GROUP BY Event.eventID
            ORDER BY Event.date DESC
        """
        
        with sql.connect(dbName, check_same_thread=False) as conn:
            response = conn.execute(my_query, (hostID,)).fetchall()
		
        if response:
            result = []
            for row in response:
                event = {
                    "Event ID": row[0],
                    "Name": row[1],
                    "Date": row[2],
                    "Time": row[3],
                    "Location": f"{row[4]}, {row[5]}, {row[6]}",
                    "Tickets Sold": row[7]
                }
                result.append(event)
            
            return jsonify(result)
        else:
            return {"Not Found": "No events found for this host"}, 404
		







## hou u nog niet te veel bezig met HTML code, daarvoor kunnen we aan chatGPT vragen of een andere generator, 
## eerst zorgen dat API werkt (queries correct kunnen uitvoeren)
# @app.route('/')
# def home():
#     return render_template('index.html')


## add resources
api.add_resource(EventsR, '/events', '/events/<string:category>', '/events/<int:eventID>')
api.add_resource(HostEventsR, '/host/<int:hostID>/events')
# api.add_resource(UpcomingEventsR, '/upcoming')
api.add_resource(RegisterR, '/register')
api.add_resource(LoginR, '/login')
api.add_resource(LogoutR, '/logout')
api.add_resource(UsersR, '/users', '/users/<int:userID>')
api.add_resource(ShoppingCartR, '/cart/<int:userID>')



if __name__ == '__main__':
	app.run(debug=True)