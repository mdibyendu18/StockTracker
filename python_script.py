import sys

if sys.version_info[0] < 3:
	import urllib
else:
	import urllib.request
	
import os,zipfile

import csv, redis

import logging

from datetime import datetime

def validate(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")
def main():
	# Create and and configure logger
	LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
	logFile = os.getcwd() + '/' + 'py.log'
	logging.basicConfig(filename = logFile,
						level = logging.DEBUG,
						format = LOG_FORMAT,
						filemode = 'w',
						)
	logger = logging.getLogger()
	ch = logging.StreamHandler(sys.stdout)
	ch.setLevel(logging.DEBUG)
	formatter = logging.Formatter(LOG_FORMAT)
	ch.setFormatter(formatter)
	logger.addHandler(ch)

	if sys.version_info[0] < 3:
		input_date = raw_input("Enter the date format:YYYY-MM-DD: ")
	else:
		input_date = input("Enter the date format:YYYY-MM-DD")
	validate(input_date)
	dt = datetime.strptime(input_date, '%Y-%m-%d')
	day = str("{0:0=2d}".format(dt.day))
	month = str("{0:0=2d}".format(dt.month))
	year = str(abs(dt.year) % 100) 
	url = "https://www.bseindia.com/download/BhavCopy/Equity/EQ"+day+month+year+"_CSV.ZIP"

	fileName = "EQ"+day+month+year+"_CSV.ZIP"
	logger.info("Downloading Equity CSV file for: "+str(input_date))

	if sys.version_info[0] < 3:
		urllib.urlretrieve(url, fileName)
	else:
		try:
		    conn = urllib.request.urlopen(url)
		except urllib.error.HTTPError as e:
		    # Return code error (e.g. 404, 501, ...)
		    # ...
		    logger.info('HTTPError: {}'.format(e.reason))
		    exit()
		except urllib.error.URLError as e:
		    # Not an HTTP-specific error (e.g. connection refused)
		    # ...
		    logger.info('URLError: {}'.format(e.reason))
		    exit()
		else:
		    urllib.request.urlretrieve(url, fileName)
		    logger.info('Downloading '+ fileName+' completed successfully')
	# Store the current directory
	curDir = os.getcwd()
	 
	 # Extract the zip file  
	logger.info("Extracting the csv file "+fileName)    
	zipFileToExtract = zipfile.ZipFile(curDir+'/'+fileName)
	zipFileToExtract.extractall(curDir)
	zipFileToExtract.close()
	logger.info("Finished extracting file")    

	r = redis.StrictRedis()

	logger.info("Reading the CSV File")
	logger.info("Inserting records into Redis DB")

	# Open the csv file as context manager
	with open("EQ"+day+month+year+".CSV",'r') as csv_file:
		csv_reader = csv.DictReader(csv_file)
		# read each row in csv file and insert into redis Db
		for line in csv_reader:
			code 	= line["SC_CODE"]
			name 	= line["SC_NAME"]
			opening = line["OPEN"]
			high 	= line["HIGH"]
			low 	=  line["LOW"]
			close 	= line["CLOSE"]
			# combining all the stock details as python dictionary
			stock_detail = {"code": str(code), 
				"name": str(name), "open": str(opening), "high": str(high), 
				"low": str(low), "close": str(close)}
			r.hmset("stock:"+str(csv_reader.line_num), stock_detail
				)
			r.set("stock:name:"+str(name).replace(" ","").lower(), str(csv_reader.line_num))
		logger.info("Finished inserting data into Redis DB ")

if __name__ == '__main__':
    main()