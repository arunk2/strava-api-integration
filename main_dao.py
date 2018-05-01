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
		# prepare a cursor object using cursor() method
		cursor = db.cursor()

		# Drop table if it already exist using execute() method.
		cursor.execute("DROP TABLE IF EXISTS ATHLETE")

		# Create table as per requirement
		sql = """CREATE TABLE ATHLETE (
					id INT(11) NOT NULL,
					firstname  VARCHAR(50),
					lastname  VARCHAR(50),
					sex CHAR(1),
					email VARCHAR(50),
					profile VARCHAR(200),
					username VARCHAR(50),
					access_token VARCHAR(100)
					)"""

		cursor.execute(sql)
		cursor.execute("DROP TABLE IF EXISTS ACTIVITIES")

		sql = """CREATE TABLE ACTIVITIES (
					id INT(11) NOT NULL,
					athlete_id  INT(11),
					athlete_firstname VARCHAR(50),
					athlete_lastname  VARCHAR(50),
					title  VARCHAR(50),
					description  VARCHAR(100),
					start_date datetime,
					start_date_local datetime,
					type VARCHAR(10),
					distance  FLOAT,
					distance_unit VARCHAR(5),
					moving_time  FLOAT,
					elapsed_time FLOAT,
					)"""

		cursor.execute(sql)

		# disconnect from server
		db.close()


	def add_athlete(user):
		return None

	def add_activity():
		return None


