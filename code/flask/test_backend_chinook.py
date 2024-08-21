import flask
from flask import Flask, jsonify, request, redirect, render_template
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth
import sqlite3 as sql

## creating app and its API
app = Flask(__name__)
api = Api(app, prefix="/api/v1")

chinook = "Chinook.sqlite"

class display_allR(Resource):
	# The site should display available albums, including artist name, genre, album cover, price, and the number of tracks.
	def get(self):
		conn = sql.connect(chinook, check_same_thread=False)
		my_query = """SELECT al.AlbumId, al.Title AS AlbumTitle, ar.Name AS ArtistName, g.Name AS GenreName, COUNT(t.TrackId) AS NumberOfTracks, SUM(t.UnitPrice) AS TotalPrice
        FROM Album al
        INNER JOIN Artist ar ON al.ArtistId = ar.ArtistId
        INNER JOIN Track t ON al.AlbumId = t.AlbumId
        INNER JOIN Genre g ON t.GenreId = g.GenreId
        GROUP BY al.AlbumId, al.Title, ar.Name, g.Name
        ORDER BY ar.Name, al.Title;""" 
		response = conn.execute(my_query).fetchall() # response type: list
		conn.close()
		result = [ # pretty displaying retrieved data
			{
                "album": element[0],
                "title": element[1],
                "artist": element[2],
                "genre": element[3],
                "number of tracks": element[4],
                "total price": element[5]
            }
			for element in response]
		return jsonify({"events": result})
	
class display_oneR(Resource):
	# The site should display a certain album, including artist name, genre, album cover, price, and the number of tracks.
	def get(self,albumID):
		conn = sql.connect(chinook, check_same_thread=False)
		my_query = """SELECT al.AlbumId, al.Title AS AlbumTitle, ar.Name AS ArtistName, g.Name AS GenreName, COUNT(t.TrackId) AS NumberOfTracks, SUM(t.UnitPrice) AS TotalPrice
        FROM Album al
        INNER JOIN Artist ar ON al.ArtistId = ar.ArtistId
        INNER JOIN Track t ON al.AlbumId = t.AlbumId
        INNER JOIN Genre g ON t.GenreId = g.GenreId
		WHERE al.AlbumId = ?;""" 
		response = conn.execute(my_query,(albumID,)).fetchone()
		conn.close()
		if response:
			result = {
                    "album": response[0],
                    "title": response[1],
                    "artist": response[2],
                    "genre": response[3],
                    "number of tracks": response[4],
                    "total price": response[5]
            }
			return jsonify(result)
		else:
			return {"Not Found": "Album not found"}, 404
		


api.add_resource(display_allR, '/display_all')
api.add_resource(display_oneR, '/display_one/<int:albumID>')


if __name__ == '__main__':
	app.run(debug=True) # enable debug mode -> show interactive traceback in the browser when an unhandled error occurs during a request, port=8080 if you want to use a specific port number