# this is the one to run daily just after 4pm ish when the new prices come in
agile_tariff_code = 'E-1R-AGILE-18-02-21-L'  # This changes by area so choose the right one (displayed in your octopus dashboard). Codes end in A->P

import sqlite3
import datetime
import requests
import time

# Future enhancement, pass these as an array instead to save processing
# though it only runs once a day so it's not exactly important.
def insertVariableIntoTable(year, month, day, hour, segment, price):
	try:
		sqliteConnection = sqlite3.connect('/home/pi/octopus-agile-pi-prices/octoprice.sqlite')
		cursor = sqliteConnection.cursor()
		print("Connected to SQLite")

		sqlite_insert_with_param = """INSERT INTO 'prices'
			('year', 'month', 'day', 'hour', 'segment', 'price') 
						VALUES (?, ?, ?, ?, ?, ?);"""

		data_tuple = (year, month, day, hour, segment, price)
		cursor.execute(sqlite_insert_with_param, data_tuple)
		sqliteConnection.commit()
		print("1 record inserted successfully into prices table")
		cursor.close()
	except sqlite3.Error as error:
		print("Failed to insert Python variable into prices table", error)
	finally:
		if (sqliteConnection):
			sqliteConnection.close()
			print("The SQLite connection is closed. We are done here.")

def retrieveTariffs():
	try:
		response = requests.get('https://api.octopus.energy/v1/products/AGILE-18-02-21/electricity-tariffs/'+agile_tariff_code+'/standard-unit-rates/')
		pricedata = response.json()
		print(pricedata['count'])
		print(pricedata['results'][0])
	except:
		print("Error retrieving tariff data")
		return False

	#Check date of first row to see if tomorrow's prices have been returned
	firstrow=pricedata['results'][0]
	firstrawdate=firstrow['valid_from']
	firstdate=datetime.datetime.strptime(firstrawdate, "%Y-%m-%dT%H:%M:%SZ").date()
	print("Date of first row ", firstdate)
	if datetime.date.today() < firstdate: # date of first row is in the future so new prices are available
		print("New prices are available, inserting into database")

		for result in pricedata['results']:
			print(result['value_inc_vat'])
			mom_price = result['value_inc_vat']
			raw_from = result['valid_from']
					# work out the buckets
			date = datetime.datetime.strptime(raw_from, "%Y-%m-%dT%H:%M:%SZ") # We need to reformat the date to a python date from a json date
			mom_year = (date.year)
			mom_month = (date.month)
			mom_day = (date.day)
			mom_hour = (date.hour)
			if date.minute == 00: # We actually don't care about exact minutes, we just mark with a 0 if it's an hour time or a 1 if it's half past the hour.
					mom_offset = 0
			else:
					mom_offset = 1 #half hour

			# Now store in the database
			insertVariableIntoTable(mom_year, mom_month, mom_day, mom_hour, mom_offset, mom_price)
		return True
	else:
		return False

count = 0
while (count < 100):
	if retrieveTariffs(): #function returns true if successful
		print("updated prices retrieved")
		break
	else:
		print("prices not yet available, retrying in 10 mins")
		time.sleep(600)
