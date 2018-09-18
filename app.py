from typing import Tuple

from flask import Flask, jsonify, request, Response
import mockdb.mockdb_interface as db

app = Flask(__name__)


def create_response(
    data: dict = None, status: int = 200, message: str = ""
) -> Tuple[Response, int]:
    """Wraps response in a consistent format throughout the API.
    
    Format inspired by https://medium.com/@shazow/how-i-design-json-api-responses-71900f00f2db
    Modifications included:
    - make success a boolean since there's only 2 values
    - make message a single string since we will only use one message per response
    IMPORTANT: data must be a dictionary where:
    - the key is the name of the type of data
    - the value is the data itself

    :param data <str> optional data
    :param status <int> optional status code, defaults to 200
    :param message <str> optional message
    :returns tuple of Flask Response and int, which is what flask expects for a response
    """
    if type(data) is not dict and data is not None:
        raise TypeError("Data should be a dictionary 😞")

    response = {
        "code": status,
        "success": 200 <= status < 300,
        "message": message,
        "result": data,
    }
    return jsonify(response), status


"""
~~~~~~~~~~~~ API ~~~~~~~~~~~~
"""


@app.route("/")
def hello_world():
    return create_response({"content": "hello world!"})


@app.route("/mirror/<name>")
def mirror(name):
    data = {"name": name}
    return create_response(data)


# TODO: Implement the rest of the API here!
@app.route("/users", methods=["GET","POST"])
def users():
	if request.method == "GET":
		
		team = request.args.get("team")
		
		if not team:
			data = {"users": db.get("users")}
			return create_response(data)
		
		users = db.get("users")
		team_users = [u for u in users if u["team"] == team]
		data = {"users": team_users}
		
		return create_response(data)
	
	else:
		
		name = request.args.get("name")
		age = request.args.get("age")
		team = request.args.get("team")
		
		if name is None or age is None or team is None:
			return create_response(None, 422,
			"You are missing necessary parameters"
			)
		
		else:
			payload = {
				"name": name,
				"age": age,
				"team": team
			}
			
			newUser = db.create("users", payload)
			
			return create_response(newUser, 201)
			
	
@app.route("/users/<int:id>", methods=["GET","PUT","DELETE"])
def getUserFromID(id):
	
	user = db.getById("users", id)
	
	if user is None:
		return create_response(user, 404, 
		"There is no user with that ID"
		)
	
	if request.method == "GET":
	
		return create_response(user)
		
	elif request.method == "PUT":
		
		name = request.args.get("name")
		age = request.args.get("age")
		team = request.args.get("team")
		
		update_values = {
			"name": name,
			"age": age,
			"team": team
		}
		
		newUser = db.updateById("users", id, update_values)
		return create_response(newUser)
	
	elif request.method == "DELETE":
		
		db.deleteById("users", id)
		return create_response(None, 200, "You have removed user " + str(id))
		
		


"""
~~~~~~~~~~~~ END API ~~~~~~~~~~~~
"""
if __name__ == "__main__":
    app.run(debug=True)
