import flask
from flask import Flask, request, jsonify, redirect, render_template
from flask_restful import Resource, Api
import sqlite3 as sql
from flask import session


## creating app and its API
app = Flask(__name__)
app.secret_key = "mySecretKey123"  # stel een geheime sleutel in voor sessiebeveiliging
api = Api(app)

## connection to database
## !! open and close the connection as close to the actual database operations as possible !!
dbName = "autocreated.db"

## definition of classes

# resource for displaying all events or a specific event, possibility to filter based on category
class EventsR(Resource):
	def get(self, category=None, eventID=None):
		if eventID: # display specific event
			my_query = """
                SELECT 
                    Event.name AS event_name,
                    Event.date AS event_date,
                    Event.time AS event_time,
                    Location.address || ', ' || Location.zipcode || ', ' || Location.city || ', ' || Location.country AS location,
                    Event.posterURL AS poster_image,
                    TicketTier.price AS ticket_price,
                    TicketTier.remainingAmount AS tickets_remaining,
                    Event.artists AS artists_or_bands,
                    Host.name AS event_host
                FROM 
                    Event
                INNER JOIN 
                    Location ON Event.locationID = Location.locationID
                INNER JOIN 
                    Host ON Event.hostID = Host.hostID
                INNER JOIN 
                    TicketTier ON Event.eventID = TicketTier.eventID
                WHERE 
                    Event.date > date('now')
                    AND Event.eventID = ?
                ORDER BY 
                    Event.date ASC, Event.time ASC;
                """
			with sql.connect(dbName, check_same_thread=False) as conn:
				response = conn.execute(my_query, (eventID,)).fetchone() # FETCH ONE
			if response: # dus als er een event is met dit eventID
				result = {
					"Event name": response[0],
					"Date": response[1],
					"Time": response[2],
					"Location": response[3],
					"Link to poster": response[4],
					"Ticket price": response[5],
					"Tickets remaining": response[6],
					"Artists/bands": response[7],
					"Event host": response[8]
				}
				return jsonify(result)
			else:
				return {"Not Found": "Event not found"}, 404
		else:
			if category: # display events based on category
				my_query = """
                    SELECT 
                        Event.name AS event_name,
                        Event.date AS event_date,
                        Event.time AS event_time,
                        Location.address || ', ' || Location.zipcode || ', ' || Location.city || ', ' || Location.country AS location,
                        Event.posterURL AS poster_image,
                        TicketTier.price AS ticket_price,
                        TicketTier.remainingAmount AS tickets_remaining,
                        Event.artists AS artists_or_bands,
                        Host.name AS event_host
                    FROM 
                        Event
                    INNER JOIN 
                        Location ON Event.locationID = Location.locationID
                    INNER JOIN 
                        Host ON Event.hostID = Host.hostID
                    INNER JOIN 
                        TicketTier ON Event.eventID = TicketTier.eventID
                    WHERE 
                        Event.date > date('now')
						AND Event.category = ?
                    ORDER BY 
                        Event.date ASC, Event.time ASC;
                    """
				with sql.connect(dbName, check_same_thread=False) as conn:
					response = conn.execute(my_query,(category,)).fetchall() # response type: list			
			else: # display all events
				my_query = """
                    SELECT 
                        Event.name AS event_name,
                        Event.date AS event_date,
                        Event.time AS event_time,
                        Location.address || ', ' || Location.zipcode || ', ' || Location.city || ', ' || Location.country AS location,
                        Event.posterURL AS poster_image,
                        TicketTier.price AS ticket_price,
                        TicketTier.remainingAmount AS tickets_remaining,
                        Event.artists AS artists_or_bands,
                        Host.name AS event_host
                    FROM 
                        Event
                    INNER JOIN 
                        Location ON Event.locationID = Location.locationID
                    INNER JOIN 
                        Host ON Event.hostID = Host.hostID
                    INNER JOIN 
                        TicketTier ON Event.eventID = TicketTier.eventID
                    WHERE 
                        Event.date > date('now')
                    ORDER BY 
                        Event.date ASC, Event.time ASC;
                    """
				with sql.connect(dbName, check_same_thread=False) as conn:
					response = conn.execute(my_query).fetchall() # response type: list
			result = [
				{
					"Event name": element[0],
					"Date": element[1],
					"Time": element[2],
					"Location": element[3],
					"Link to poster": element[4],
					"Ticket price": element[5],
					"Tickets remaining": element[6],
					"Artists/bands": element[7],
					"Event host": element[8]
				}
				for element in response
			]
			return jsonify({"events": result})
	

# register a new user
class RegisterR(Resource):
    def post(self):
        # collect new incoming user data
        username = request.json.get("username")
        password = request.json.get("password")
        email = request.json.get("email")
        firstName = request.json.get("firstName")
        lastName = request.json.get("lastName")
        userType = request.json.get("userType") # host/customer, provide dropdown menu in HTML code?
        hostName = request.json.get("hostName") # only required if userType is "host"
		
        # check whether user already exists
        conn = sql.connect(dbName, check_same_thread=False)

        my_query = """SELECT * FROM User WHERE username=?"""
        response = conn.execute(my_query, (username,)).fetchone() # als response == 0 is het een nieuwe user die wilt registreren
        if response:
            return {"Bad Request": "Username already taken"}, 400

        # insert new user
        cursor = conn.cursor()
        # insert new user into the User table
        cursor.execute("INSERT INTO User (username, password, email) VALUES (?, ?, ?)", (username, password, email))
        conn.commit()

        userID = cursor.lastrowid # get the userID of newly added user

        # insert into Host or Customer table based on userType
        if userType == "host":
            if not hostName:  # ensure hostName is provided
                conn.close()
                return {"Bad Request": "Host name is required for host userType"}, 400
            
            # insert into the Host table
            cursor.execute("INSERT INTO Host (userID, name) VALUES (?, ?)",(userID, hostName))
        elif userType == "customer":
            # insert into the Customer table
            cursor.execute("INSERT INTO Customer (userID, firstName, lastName) VALUES (?, ?, ?)",(userID, firstName, lastName))
        else:
            conn.close()
            return {"Bad Request": "Invalid user type"}, 400

        conn.commit()
        conn.close()
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
					"email": response[3]
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
					"email": element[3]
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
			my_query = """SELECT PurchaseItem.quantity, TicketTier.description, TicketTier.price, Event.name
              FROM PurchaseItem
              INNER JOIN TicketTier ON PurchaseItem.ticketTierID = TicketTier.ticketTierID
              INNER JOIN Event ON TicketTier.eventID = Event.eventID
			  INNER JOIN Customer ON PurchaseItem.customerID = Customer.customerID
              WHERE Customer.userID = ?"""

			with sql.connect(dbName, check_same_thread=False) as conn:
				response = conn.execute(my_query, (userID,)).fetchall() # neem de hele shopping cart
			if response: # dus geen lege shopping cart
				result = [
                    {
                        "Quantity": element[0],
                        "Ticket tier": element[1],
                        "Ticket price": element[2],
                        "Event name": element[3]
                    }
                    for element in response]
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
		
        
		# voeg item toe aan cart
		#1- zoek customerID
		conn = sql.connect(dbName, check_same_thread=False)
		cursor = conn.cursor()
		response = cursor.execute("""SELECT Customer.customerID 
							  FROM Customer 
							  INNER JOIN User ON User.userID = Customer.userID
							  WHERE User.userID = ?""", (userID,)).fetchone()
		if response:
			customerID = response[0] # fetch customerID based on given userID
		else:
			return {"Not Found": "User not found"}, 404
	

		#2- get ticketTierID based on eventName and ticketTier
		my_query = """SELECT TicketTier.ticketTierID FROM TicketTier
                      INNER JOIN Event ON TicketTier.eventID = Event.eventID
                      WHERE Event.name = ? AND TicketTier.description = ?"""
		ticket = cursor.execute(my_query, (eventName, ticketTier)).fetchone()
		if not ticket:  # if the ticket does not exist
			conn.close()
			return {"Bad Request": "Invalid event name or ticket tier"}, 400
		ticketTierID = ticket[0]

        # insert new item
		my_query = """INSERT INTO PurchaseItem (customerID, ticketTierID, quantity) VALUES (?,?,?)"""
		cursor.execute(my_query, (customerID, ticketTierID, quantity))
		conn.commit()
		purchaseItemID = cursor.lastrowid # get purchaseItemID of the newly added cart item
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