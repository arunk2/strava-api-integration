from stravalib.client import Client
from flask import Flask, jsonify, request
import json
import CONSTANTS
from main_dao import MainDAO

app = Flask(__name__)
app.url_map.strict_slashes = False


def health_check():
	return jsonify({"status": "success"})


def login():
	client = Client()
	authorize_url = client.authorization_url(client_id=CONSTANTS.CLIENT_ID, 
											redirect_uri=CONSTANTS.CALLBACK_URL)
	# Have the user click the authorization URL, 
	# a 'code' param will be added to the redirect_uris
	return jsonify({"status": "success", "url": authorize_url})


def authorized_callback():
	client = Client()
	# Extract the code from your webapp response
	code = request.args.get('code')
	access_token = client.exchange_code_for_token(client_id=CONSTANTS.CLIENT_ID, 
												client_secret=CONSTANTS.CLIENT_SECRET, 
												code=code)
	# Now store that access token along with athlete details
	print(access_token)
	add_athlete(access_token)
	return jsonify({"status": "success"})


def get_athletes():
	dao = MainDAO()
	result = dao.get_athletes()
	return jsonify({"status": "success", "athletes": result})


def get_activities():
	dao = MainDAO()
	result = dao.get_activities()
	return jsonify({"status": "success", "activities": result})


def dump_activities():
	dao = MainDAO()
	result = dao.get_athletes()
	for athlete in result:
		access_token = athlete['access_token']
		pull_activities(access_token, athlete['firstname'], athlete['lastname'], today.strftime("%Y-%B-%d")+'T00:00:00Z')
	return jsonify({"status": "success"})


def create_db():
	dao = MainDAO()
	dao.create_db()
	return jsonify({"status": "success"})


def add_athlete(access_token):
	# An authorized callback is coming. Process it and add 
	client = Client()

	# Now store that access token along with athlete details
	client.access_token = access_token
	athlete = client.get_athlete()
	ath = extract_athlete(athlete)
	ath['access_token'] = access_token
	print(ath)
	dao = MainDAO()
	dao.add_athlete(ath)
	from datetime import datetime
	today = datetime.now()
	pull_activities(access_token, ath['firstname'], ath['lastname'])
	return True


def extract_athlete(athlete):
	ath = {}
	try:
		ath['id'] = athlete.id
		ath['firstname'] = athlete.firstname
		ath['lastname'] = athlete.lastname
		ath['sex'] = athlete.sex
		ath['email'] = athlete.email
		ath['profile'] = athlete.profile
		ath['username'] = athlete.username
	except Exception as excep:
		print(excep)

	return ath


def pull_activities(access_token, firstname, lastname, from_time = "2018-01-01T00:00:00Z"):
	# An authorized callback is coming. Process it and add 
	client = Client()
	client.access_token = access_token
	for activity in client.get_activities(after = from_time,  limit=500):
		process_activity(activity, firstname, lastname)
		
	return True


def process_activity(activity, firstname, lastname):
	act = extract_activity(activity)
	act['athlete_firstname'] = firstname
	act['athlete_lastname'] = lastname
	print(act)
	dao = MainDAO()
	dao.add_activity(act)


def extract_activity(activity):
	try:
		act = {}
		act['id'] = activity.id
		act['athlete_id'] = activity.athlete.id
		act['athlete_firstname'] = activity.athlete.firstname
		act['athlete_lastname'] = activity.athlete.lastname
		act['title'] = activity.name
		act['description'] = activity.description
		act['type'] = activity.type
		act['distance'] = activity.distance.get_num()
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
	except Exception as excep:
		print(excep)
	return act


@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response


app.add_url_rule(rule='/health', endpoint='health-check', view_func=health_check, methods=['GET'])
app.add_url_rule(rule='/login', endpoint='login', view_func=login, methods=['GET'])
app.add_url_rule(rule='/authorized', endpoint='authorized-callback', view_func=authorized_callback, methods=['GET'])
app.add_url_rule(rule='/dump_activities', endpoint='dump-activities', view_func=dump_activities, methods=['GET'])
app.add_url_rule(rule='/create_db', endpoint='create_db', view_func=create_db, methods=['GET'])

app.add_url_rule(rule='/athletes', endpoint='get-athletes', view_func=get_athletes, methods=['GET'])
app.add_url_rule(rule='/activities', endpoint='get-activities', view_func=get_activities, methods=['GET'])


if __name__ == '__main__':
	app.run(debug=True, host='localhost', port=8082)
