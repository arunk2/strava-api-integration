from stravalib.client import Client
from flask import Flask, jsonify, request
import json
import CONSTANTS

app = Flask(__name__)
app.url_map.strict_slashes = False


def login():
	client = Client()
	authorize_url = client.authorization_url(client_id=CONSTANTS.CLIENT_ID, 
											redirect_uri=CONSTANTS.CALLBACK_URL)
	# Have the user click the authorization URL, a 'code' param will be added to the redirect_uris
	return jsonify({"message": "success", "url": authorize_url})


def authorized_callback():
	client = Client()
	# Extract the code from your webapp response
	code = request.args.get('code') # or whatever your framework does
	access_token = client.exchange_code_for_token(client_id=CONSTANTS.CLIENT_ID, 
												client_secret=CONSTANTS.CLIENT_SECRET, code=code)

	# Now store that access token along with athlete details
	print(access_token)
	add_athlete(access_token)

	return jsonify({"message": "success"})


def dump_activities():
	return jsonify({"message": "success"})


def add_athlete(access_token):
	# An authorized callback is coming. Process it and add 
	client = Client()

	# Now store that access token along with athlete details
	client.access_token = access_token
	athlete = client.get_athlete()

	print("For {id}, I now have an access token {token}".format(id=athlete.id, token=access_token))
	print(dir(athlete))
	print(athlete.to_dict())
	# add_athlte(athlete)

	# for activity in client.get_activities(after = "2010-01-01T00:00:00Z",  limit=2):
	# 	process_activity(activity)

	get_activities(access_token)

	return True


def get_activities(access_token):
	# An authorized callback is coming. Process it and add 
	client = Client()
	client.access_token = access_token
	for activity in client.get_activities(after = "2010-01-01T00:00:00Z",  limit=2):
		process_activity(activity)
		
	return jsonify({"message": "success"})


def process_activity(activity):
	act = {}
	act['id'] = activity.id
	act['athlete_id'] = activity.athlete.id
	act['athlete_fname'] = activity.athlete.firstname
	act['athlete_lname'] = activity.athlete.lastname
	act['name'] = activity.name
	act['description'] = activity.description
	act['type'] = activity.type
	act['distance_num'] = activity.distance.get_num()
	act['distance_unit'] = activity.distance.get_unit().get_specifier()
	act['moving_time'] = round(activity.moving_time.total_seconds()/60.0)
	act['elapsed_time'] = round(activity.elapsed_time.total_seconds()/60.0)
	act['start_date'] = activity.start_date
	act['start_date_local'] = activity.start_date_local

	# act['location_city'] = activity.location_city
	# act['location_country'] = activity.location_country
	# act['location_state'] = activity.location_state	
	# act['start_date'] = activity.start_date
	# act['start_date_local'] = activity.start_date_local
	# act['start_latitude'] = activity.start_latitude
	# act['start_latlng'] = activity.start_latlng
	# act['start_longitude'] = activity.start_longitude
	# act['workout_type'] = activity.workout_type
	print(act)


def health_check():
	return jsonify({"message": "success"})


app.add_url_rule(rule='/health', endpoint='health-check', view_func=health_check, methods=['GET'])
app.add_url_rule(rule='/login', endpoint='login', view_func=login, methods=['GET'])
app.add_url_rule(rule='/authorized', endpoint='authorized-callback', view_func=authorized_callback, methods=['GET'])
app.add_url_rule(rule='/dump_activities', endpoint='dump-activities', view_func=dump_activities, methods=['GET'])


if __name__ == '__main__':
	app.run(debug=True, host='localhost', port=8082)
