from stravalib.client import Client
from flask import Flask, jsonify, request, redirect
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
	token_response = client.exchange_code_for_token(client_id=CONSTANTS.CLIENT_ID,
												client_secret=CONSTANTS.CLIENT_SECRET,
												code=code)
	# Now store that access token along with athlete details
	# add_athlete(access_token)
	# Now store that access token along with athlete details
	access_token = token_response['access_token']
	refresh_token = token_response['refresh_token']
	expires_at = token_response['expires_at']

	client.access_token = access_token
	athlete = client.get_athlete()
	ath = extract_athlete(athlete)
	ath['access_token'] = access_token
	ath['refresh_token'] = refresh_token
	ath['expires_at'] = expires_at
	dao = MainDAO()
	dao.add_athlete(ath)
	pull_activities(access_token, refresh_token, ath['id'], ath['firstname'], ath['lastname'])

	return redirect(CONSTANTS.UI_HOMEPAGE_URL, code=302)


def get_athletes():
	dao = MainDAO()
	result = dao.get_athletes()
	for athlete in result:
		athlete['access_token'] = ''
		athlete['email'] = ''
		athlete['username'] = ''
	return jsonify({"status": "success", "athletes": result})


def get_activities():
	dao = MainDAO()
	from datetime import datetime, timedelta
	today = datetime.now() - timedelta(days=45)
	from_date = today.strftime("%Y-%m-%d")
	result = dao.get_activities(from_date)
	return jsonify({"status": "success", "activities": result})


def dump_activities():
	dao = MainDAO()
	result = dao.get_athletes()
	from datetime import datetime, timedelta
	today = datetime.now() - timedelta(days=30)
	from_date = today.strftime("%Y-%m-%d")
	from_date += 'T00:00:00Z'
	print(from_date)
	for athlete in result:
		access_token = athlete['access_token']
		refresh_token = athlete['refresh_token']
		pull_activities(access_token, refresh_token, athlete['id'], athlete['firstname'], athlete['lastname'], from_date)
	return jsonify({"status": "success"})


def create_db():
	dao = MainDAO()
	dao.create_database()
	return jsonify({"status": "success"})


def add_athlete(access_token):
	# An authorized callback is coming. Process it and add
	client = Client()

	# Now store that access token along with athlete details
	client.access_token = access_token
	athlete = client.get_athlete()
	ath = extract_athlete(athlete)
	ath['access_token'] = access_token
	dao = MainDAO()
	dao.add_athlete(ath)
	pull_activities(access_token, ath['firstname'], ath['lastname'])
	return True


def extract_athlete(athlete):
	ath = {}
	try:
		ath['id'] = athlete.id
		ath['firstname'] = athlete.firstname
		ath['lastname'] = athlete.lastname if athlete.lastname else ""
		ath['sex'] = athlete.sex
		ath['email'] = athlete.email
		ath['profile'] = athlete.profile
		ath['username'] = athlete.username
	except Exception as excep:
		print(excep)

	return ath


def pull_activities(access_token, refresh_token, id, firstname, lastname, from_time = "2022-01-01T00:00:00Z"):
	# An authorized callback is coming. Process it and add
	client = Client()
	refresh_response = client.refresh_access_token(client_id=CONSTANTS.CLIENT_ID, client_secret=CONSTANTS.CLIENT_SECRET,
												   refresh_token = refresh_token)

	ath = {}
	ath['access_token'] = refresh_response['access_token']
	ath['refresh_token'] = refresh_response['refresh_token']
	ath['expires_at'] = refresh_response['expires_at']
	ath['id'] = id
	dao = MainDAO()
	dao.update_athlete(ath)

	client.access_token = refresh_response['access_token']
	client.refresh_token = refresh_response['refresh_token']

	for activity in client.get_activities(after = from_time,  limit=500):
		process_activity(activity, firstname, lastname)

	return True


def process_activity(activity, firstname, lastname):
	act = extract_activity(activity)
	act['athlete_firstname'] = firstname
	act['athlete_lastname'] = lastname
	dao = MainDAO()
	dao.add_activity(act)


def extract_activity(activity):
	try:
		act = {}
		act['id'] = activity.id
		act['athlete_id'] = activity.athlete.id
		act['athlete_firstname'] = activity.athlete.firstname
		act['athlete_lastname'] = activity.athlete.lastname
		act['title'] = str(activity.name.encode('ascii', 'ignore')).replace("'", "")
		act['description'] = activity.description
		act['type'] = activity.type
		act['distance'] = activity.distance
		act['distance_unit'] = "m"
		act['moving_time'] = activity.moving_time
		act['elapsed_time'] = activity.elapsed_time
		act['start_date'] = activity.start_date
		act['start_date_local'] = activity.start_date_local

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
