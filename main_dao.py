#!/usr/bin/python

import MySQLdb
import CONSTANTS


class MainDAO():
	def __init__(self):
		self.host = CONSTANTS.DB_HOST
		self.user = CONSTANTS.DB_USER
		self.password = CONSTANTS.DB_PASS
		self.database = CONSTANTS.DB_DATABASE

	def create_database(self):
		# Open database connection
		db = MySQLdb.connect(self.host, self.user, self.password, self.database)

		try:
			# prepare a cursor object using cursor() method
			cursor = db.cursor()

			# Drop table if it already exist using execute() method.
			cursor.execute("DROP TABLE IF EXISTS ATHLETE")

			# Create table as per requirement
			sql = """CREATE TABLE ATHLETE (
						id BIGINT NOT NULL PRIMARY KEY,
						firstname  VARCHAR(50),
						lastname  VARCHAR(50),
						sex CHAR(1),
						email VARCHAR(50),
						profile VARCHAR(200),
						username VARCHAR(50),
						access_token VARCHAR(100),
						refresh_token VARCHAR(100),
						expires_at VARCHAR(100)
						)"""

			print(sql)

			cursor.execute(sql)
			cursor.execute("DROP TABLE IF EXISTS ACTIVITIES")

			sql = """CREATE TABLE ACTIVITIES (
						id BIGINT NOT NULL PRIMARY KEY,
						athlete_id  INT(11),
						athlete_firstname VARCHAR(50),
						athlete_lastname  VARCHAR(50),
						title  VARCHAR(50),
						description  VARCHAR(100),
						start_date datetime,
						start_date_local datetime,
						type VARCHAR(10),
						distance  VARCHAR(25),
						distance_unit VARCHAR(5),
						moving_time  VARCHAR(25),
						elapsed_time VARCHAR(25)
						)"""

			print(sql)

			cursor.execute(sql)
			# Commit your changes in the database
			db.commit()
		except:
		   # Rollback in case there is any error
		   db.rollback()

		# disconnect from server
		db.close()


	def add_athlete(self, user):
		# Open database connection
		db = MySQLdb.connect(self.host, self.user, self.password, self.database)

		try:
			# prepare a cursor object using cursor() method
			cursor = db.cursor()

			sql = """INSERT INTO ATHLETE (id, firstname, lastname, sex, email, profile, username, access_token, 
			refresh_token, expires_at)
							VALUES ({id}, '{firstname}', '{lastname}', '{sex}', '{email}', '{profile}', '{username}', 
							'{access_token}', '{refresh_token}', '{expires_at}'
							)""".format(id=user['id'], firstname=user['firstname'],
										lastname=user['lastname'], sex=user['sex'],
										email=user['email'], profile=user['profile'],
										username=user['username'], access_token=user['access_token'],
										refresh_token=user['refresh_token'], expires_at=user['expires_at'])

			print(sql)

			cursor.execute(sql)
			# Commit your changes in the database
			db.commit()
		except Exception as exception:
			print(exception)
			db.rollback()

		# disconnect from server
		db.close()
		return True


	def update_athlete(self, user):
		# Open database connection
		db = MySQLdb.connect(self.host, self.user, self.password, self.database)

		try:
			# prepare a cursor object using cursor() method
			cursor = db.cursor()

			sql = """UPDATE ATHLETE SET access_token = {access_token}, 
										refresh_token = {refresh_token}, 
										expires_at = {expires_at}
										WHERE id = {id}
							)""".format(id=user['id'], access_token=user['access_token'],
										refresh_token=user['refresh_token'], expires_at=user['expires_at'])

			print(sql)
			cursor.execute(sql)
			# Commit your changes in the database
			db.commit()
		except Exception as exception:
			print(exception)
			db.rollback()

		# disconnect from server
		db.close()
		return True

	def add_activity(self, activity):
		# Open database connection
		db = MySQLdb.connect(self.host, self.user, self.password, self.database)

		try:
			# prepare a cursor object using cursor() method
			cursor = db.cursor()

			sql = """INSERT INTO ACTIVITIES (id, athlete_id, athlete_firstname, athlete_lastname,
							title, description, start_date, start_date_local, type, distance,
							distance_unit, moving_time, elapsed_time)
							VALUES ({id}, {athlete_id}, '{athlete_firstname}', '{athlete_lastname}',
							'{title}', '{description}', '{start_date}', '{start_date_local}', '{type}',
							'{distance}', '{distance_unit}', '{moving_time}',
							'{elapsed_time}')""".format(id=activity['id'], athlete_id=activity.get('athlete_id', ''),
										athlete_firstname=activity.get('athlete_firstname'), athlete_lastname=activity.get('athlete_lastname'),
										title=activity.get('title'), description=activity.get('description'),
										start_date=activity.get('start_date'), start_date_local=activity.get('start_date_local'),
										type=activity.get('type'), distance=activity.get('distance'), distance_unit=activity.get('distance_unit'),
										moving_time=activity.get('moving_time'), elapsed_time=activity.get('elapsed_time'))


			print(sql)
			res = cursor.execute(sql)
			print(res)
			# Commit your changes in the database
			db.commit()
		except Exception as exception:
			print(exception)
			db.rollback()

		# disconnect from server
		db.close()
		return True


	def get_athletes(self):
		# Open database connection
		db = MySQLdb.connect(self.host, self.user, self.password, self.database)

		# prepare a cursor object using cursor() method
		cursor = db.cursor()

		athletes = []
		sql = "SELECT DISTINCT id, firstname, lastname, sex, email, profile, username, access_token, refresh_token FROM ATHLETE ORDER BY firstname"
		try:
			# Execute the SQL command
			cursor.execute(sql)
			# Fetch all the rows in a list of lists.
			results = cursor.fetchall()
			for row in results:
				athlete = {}
				athlete['id'] = row[0]
				athlete['firstname'] = row[1]
				athlete['lastname'] = row[2]
				athlete['sex'] = row[3]
				athlete['email'] = row[4]
				athlete['profile'] = row[5]
				athlete['username'] = row[6]
				athlete['access_token'] = row[7]
				athlete['refresh_token'] = row[8]
				athletes.append(athlete)

		except Exception as exception:
			print(exception)
			print("Error: unable to fecth data")

		# disconnect from server
		db.close()
		return athletes


	def get_activities(self, from_date="2018-05-01"):
		# Open database connection
		db = MySQLdb.connect(self.host, self.user, self.password, self.database)

		# prepare a cursor object using cursor() method
		cursor = db.cursor()

		activities = []
		sql = "SELECT DISTINCT id, athlete_id, athlete_firstname, athlete_lastname, \
				title, description, start_date, start_date_local, type, \
				distance, distance_unit, moving_time, elapsed_time \
				FROM ACTIVITIES \
				WHERE start_date_local > '"+from_date+"' ORDER BY start_date_local DESC"
		try:
			# Execute the SQL command
			cursor.execute(sql)
			# Fetch all the rows in a list of lists.
			results = cursor.fetchall()
			for row in results:
				activity = {}
				activity['id'] = row[0]
				activity['athlete_id'] = row[1]
				activity['athlete_firstname'] = row[2]
				activity['athlete_lastname'] = row[3]
				activity['title'] = row[4]
				activity['description'] = row[5]
				activity['start_date'] = row[6].strftime("%Y-%B-%d")
				activity['start_date_local'] = row[7].strftime("%Y-%B-%d")
				activity['type'] = row[8]
				activity['distance'] = row[9]
				if "meter" in row[9]: #Split and convert to KM
					dist = row[9].split()
					activity['distance'] = str(round(float(dist[0]) / 1000.0, 2))
					activity['distance'] += " km"
				activity['distance_unit'] = row[10]
				activity['moving_time'] = row[11]
				activity['elapsed_time'] = row[12]
				if activity['title'][0] == 'b':
					activity['title'] = activity['title'][1:]
				activities.append(activity)

		except Exception as exception:
			print(exception)
			print("Error: unable to fecth data")

		# disconnect from server
		db.close()
		return activities
