# Aid data exchange
import json
# Forks processes to retrieve parameter values through shell commands
import os
# Handle threads of this process
import threading
# Despatch HTTP requests as a client
import requests
# Handle communications with a MySQL database
import MySQLdb
# Generate timestamps
import datetime
# Handle timezones
import pytz
# Handle sleeps and delays
import time
# Handle output of executing python commands stored as strings in the dictionary
import sys
# Handle output of executing python commands stored as strings in the dictionary
import StringIO
# Handle output of executing python commands stored as strings in the dictionary
import contextlib

import common
import equipment

# toDo: Read local timezone from the configuration file
timezoneLocal = pytz.timezone('Asia/Calcutta')

def universal2local(timeUniversal):
	timeLocal = timeUniversal.replace(tzinfo=pytz.utc).astimezone(timezoneLocal)
	return timezoneLocal.normalize(timeLocal).strftime('%Y-%m-%d %H:%M:%S.%f %Z%z')

# Handle output of executing python commands stored as strings in the dictionary
@contextlib.contextmanager
def stdoutIO(stdout=None):
	old = sys.stdout
	if stdout is None:
		stdout = StringIO.StringIO()
	sys.stdout = stdout
	yield stdout
	sys.stdout = old

# A class to represent the software configuration of this system
class configurationS(object):
	# The constructor for the configurationS class
	def __init__(self):
		super(configurationS, self).__init__()
		# Settings is the entire JSON-formatted content of the configuration file
		self.settings = []
		# A list of names of all measurements from every set, unique
		self.measurements = []
		# A list of values of all measurements, having a corresponding index as the name
		self.measurementValues = []
		# A list of all measurement sets, i.e. a group of names of measurements of interest to a particular element that will receive a corresponding group of values of measurements
		self.measurementSets = {}
		# The number of unique measurements, since measurements may be common across sets
		self.measurementCount = 0
		# A list of identifiers of all servers specified to accept energy data
		self.servers = {}
		# A list of all server-measurementSet combinations
		self.combinations = {}
		# The number of server-measurementSet combinations
		self.combinationCount = 0
	def cancel(self):
		self.measurementValues = []
	# A handler function to retrieve settings for the client software from a configuration file
	def load(self, filename):
		# Open the JSON-formatted configuration file
		with open(filename) as filehandle:
			# Translate JSON to a dictionary and copy it to the object of the defined class
			self.settings = json.load(filehandle)
		# Close the configuration file
		filehandle.close()
		# Digest the configuration dictionary
		# Get all the servers
		self.servers = self.settings['servers']
		# Get all the measurement sets
		self.measurementSets = self.settings['measurementSets']
		# Get all the server - measurement set combinations
		self.combinations = self.settings['combinations']
		# Declare temporary variables to traverse the combination dictionary
		combination = {}
		combinationIndex = 0;
		# Traverse the combination dictionary
		while combination != None:
			# Attempt to identify a combination ...
			try:
				combination = self.combinations['combination' + str(combinationIndex)]
			# ... unless it does not exist ...
			except KeyError:
				# ... in which case the traversal needs to be stopped ...
				combination = None
			# ...or else, get all variables whose measurements are required
			else:
				variables = self.settings['measurementSets'][str(combination['measurementSet'])]
				# Declare temporary variables for use when making a list of unique variables
				variable = {}
				variableIndex = 0
				# Traverse the variables dictionary
				while variable != None:
					# Attempt to identify a variable ...
					try:
						variable = variables['variable' + str(variableIndex)]
					# ... unless it does not exist ...
					except KeyError:
						variable = None
					# ... or else, append it to the list if not already present ...
					else:
						if str(variable) not in self.measurements:
							self.measurements.append(str(variable))
					# ... before moving on to the next variable, if any
					variableIndex += 1
			# ... before moving on to the next combination, if any
			combinationIndex += 1
		# Summarize a count of combinations and measurements
		self.combinationCount = combinationIndex
		self.measurementCount = len(self.measurements)

# A class to represent the hardware configuration of this system
class configurationH(object):
	# The constructor for the configurationH class
	def __init__(self):
		super(configurationH, self).__init__()
		# List of host hardware supported by this version of the software
		self.devices = {
			0: ('SMA Solar Technology', 'Sunny Boy', 'inverterSunnyBoy'),
			1: ('SMA Solar Technology', 'Sunny Web Box', 'loggerSunnyWebBox'),
			2: ('Helios Systems', 'HS100', 'inverterHelios'),
			3: ('Enertech', '<blank>'),
			4: ('Danfoss', '<blank>'),
			5: ('Statcon Energiaa', 'SMB096', 'combinerSMB096'),
			6: ('Beijing EPSolar Technology', 'TracerA', 'chargerTracerA'),
			7: ('Delta Electronics', 'RPI', 'inverterRPI'),
			8: ('ABB', 'PVS800', 'inverterPVS800')
		}
		# An instance of a host
		self.device = ''
		# Type of the host
		self.deviceType = ''
		# Manufacturer of the host
		self.manufacturer = ''
		# Model number of the host
		self.modelNumber = 0
		# Serial number of the host
		self.serialNumber = 0
		# Software unique identifier for the host
		self.identity = {}
		# Flag to indicate load status
		self.isLoaded = -1
		# Flag to indicate attach status
		self.isAttached = -1
		# Flag to indicate local storage
		self.toStore = ''
	# A handler function to retrieve settings for the hardware from a configuration file
	def load(self, filename):
		# Open the JSON-formatted configuration file
		with open(filename) as filehandle:
			# Translate JSON to a dictionary and copy it to the object of the defined class
			settings = json.load(filehandle)
			self.deviceType = settings['type']
			self.manufacturer = settings['manufacturer']
			self.modelNumber = settings['modelNumber']
			self.serialNumber = settings['serialNumber']
			self.identity = settings['identity']
			self.toStore = settings['toStore']
			# Raise the load status flag
			self.isLoaded = 0
		# Close the configuration file
		filehandle.close()
		# Return the load status flag
		return self.isLoaded
	# A handler function to populate the instance of the host within the instance of this class
	def attach(self):
		# Unless the host has been loaded, attach is not possible
		if self.isLoaded == -1:
			print 'Attach Hardware Configuration Fail - Load incorrect'
		else:
			# Declare temporary variables for use when attaching the host to the software
			deviceIndex = -1
			# Identify the index of the loaded host
			for key, value in cH.devices.items():
				if (value[0] == cH.manufacturer) & (value[1] == cH.modelNumber):
					deviceIndex = key
					# Raise attach status flag to indicate that the loaded host can be attached
					self.isAttached = 1
			# Unless host can be attached, attach is not possible
			if self.isAttached == 1:
				# Initialize the loaded host that needs to be attached
				with stdoutIO() as s:
					exec('self.device = equipment.' + self.devices[deviceIndex][2] + '()')
				# Attach the host
				self.device.attach(self.identity)
				# Raise attach status flag to indicate that the loaded host has also been attached
				self.isAttached = 0
			else:
				print 'Attach Hardware Configuration Fail - Host unrecognized'
		# Return the attach status flag
		return self.isAttached
	# A handler function to read the value of a variable from the host or the Raspberry Pi
	def read(self, measurementName):
		# Attempt to check if the host offers the measurement ...
		try:
			measurementIndex = [key for key, value in self.device.labels.items() if value == measurementName][0]
		# ... unless it doesn't exist ...
		except IndexError:
			# ... in which case, attempt to check if the Raspberry Pi offers the measurement ...
			try:
				measurementValue = common.getParameterHandler(measurementName)
			# ... unless it doesn't ...
			except KeyError:
				# ... in which case, take it light ...
				return -1
			else:
				# ... or return it otherwise ...
				return measurementValue
		else:
			# ... and if it does, then fetch it
			return self.device.read(measurementIndex)
	# A handler function to flush a set of measurements to read afresh in the next iteration
	def cancel(self):
		self.device.cancel()

if __name__ == '__main__':
	cH = configurationH()
	cS = configurationS()
	# Load the software configuration
	cS.load('/home/pi/marshal/cS.json')
	# Load the hardware configuration
	cH.load('/home/pi/marshal/cH.json')
	# Attach the hardware device
	cH.attach()
	# Cancel all measurements
	cS.cancel()
	cH.cancel()
	# Retrieve the measurements for all unique variables
	for measurementName in cS.measurements:
		cS.measurementValues.append(str(cH.read(measurementName)))
	# toNote: Filter checks must not be universal
	# If the filter has been triggered, exit
	# if cH.device.sanity == -1:
	# 	exit()
	# toDo: if cH.toStore is set, then log locally
	# Traverse the combination dictionary
	for combinationIndex in range(0, cS.combinationCount - 1):
		# Sequentially get each combination
		combination = cS.combinations['combination' + str(combinationIndex)]
		# Identify the server for that combination
		server = cS.servers[combination['server']]
		# Identify the measurements for that combination
		variables = cS.measurementSets[combination['measurementSet']]
		# Compose the dispatch payload that consists of ...
		requestPayload = {}
		# ... the set of measurements, ...
		measurementData = {}
		# Declare temporary variables for use when composing the payload of measurements
		variableName = ''
		variableIndex = 0
		# Traverse the list of measurements required for this combination
		while variableName != None:
			# Attempt to sequentially retrieve names of variables required for this combination ...
			try:
				if cH.device.sanity == -1:
					variableName = variables['variableAlternate' + str(variableIndex)]
				else:
					variableName = variables['variable' + str(variableIndex)]
			# ... until the end is reached ...
			except KeyError:
				# ... in which case the traversal needs to be stopped ...
				variableName = None
			# ... or else, add the measurement to the dispatch payload ...
			else:
				measurementData[str(variableName)] = cS.measurementValues[cS.measurements.index(str(variableName))]
			# ... before moving to the next variable, if any
			variableIndex += 1
		# ... the description of the host, as an indicator of how to parse the measurements, ...
		hostData = {}
		hostData['type'] = cH.deviceType
		hostData['serialNumber'] = cH.serialNumber
		hostData['manufacturer'] = cH.manufacturer
		hostData['modelNumber'] = cH.modelNumber
		hostData['toStore'] = cH.toStore
		hostData['isOnDemand'] = 'False'
		hostData['isSane'] = cH.device.sanity
		# ... and the timestamp
		# requestPayload['t'] = str(datetime.datetime.now())
		requestPayload['t'] = universal2local(datetime.datetime.now()).strip(' IST+0530')
		requestPayload['h'] = hostData
		requestPayload['m'] = measurementData
		if variableIndex == 1:
			exit()
		# If the server accepts HTTP
		if server['protocol'] == 'http':
			# Beware of self-signed certificates ...
			if not server['certificate']:
				# ... and port numbers
				if not server['portnumber']:
					response = requests.post(server['protocol'] + "://" + server['hostname'] + server['path'], auth=(server['username'], server['password']), json=requestPayload)
				else:
					response = requests.post(server['protocol'] + "://" + server['hostname'] + ":" + server['portnumber'] + server['path'], auth=(server['username'], server['password']), json=requestPayload)
			else:
				if not server['portnumber']:
					response = requests.post(server['protocol'] + "://" + server['hostname'] + server['path'], auth=(server['username'], server['password']), json=requestPayload, verify=server['certificate'])
				else:
					response = requests.post(server['protocol'] + "://" + server['hostname'] + ":" + server['portnumber'] + server['path'], auth=(server['username'], server['password']), json=requestPayload, verify=server['certificate'])
			# When the server requires additional data on-demand, marshal it
			responsePayload = json.JSONDecoder().decode(response.text)
			# Reset the measurement dictionary
			measurementData = {}
			# Create temporary variables to find out what additional data the server requires
			variableName = ''
			variableIndex = 0
			# Parse the response content
			while variableName != None:
				# Attempt to identify a variable ...
				try:
					variableName = responsePayload['variable' + str(variableIndex)]
				# ... unless it does not exist ...
				except KeyError:
					variableName = None
				# ... or else, populate the measurement dictionary of the follow-up request ...
				else:
					measurementData[str(variableName)] = cH.read(str(variableName))
				# ... before moving on to the next variable, if any
				variableIndex += 1
			# If there are on-demand measurements, shoot the follow-up request
			if variableIndex > 1:
				# Compose the dispatch payload that consists of the set of measurements, the description of the host, as an indicator of how to parse the measurements, and the timestamp
				hostData['isOnDemand'] = "True"
				# requestPayload['t'] = str(datetime.datetime.now())
				requestPayload['t'] = universal2local(datetime.datetime.now()).strip(' IST+0530')
				requestPayload['h'] = hostData
				requestPayload['m'] = measurementData
				# Beware of self-signed certificates ...
				if not server['certificate']:
					# ... and port numbers
					if not server['portnumber']:
						response = requests.post(server['protocol'] + "://" + server['hostname'] + server['path'], auth=(server['username'], server['password']), json=requestPayload)
					else:
						response = requests.post(server['protocol'] + "://" + server['hostname'] + ":" + server['portnumber'] + server['path'], auth=(server['username'], server['password']), json=requestPayload)
				else:
					if not server['portnumber']:
						response = requests.post(server['protocol'] + "://" + server['hostname'] + server['path'], auth=(server['username'], server['password']), json=requestPayload, verify=server['certificate'])
					else:
						response = requests.post(server['protocol'] + "://" + server['hostname'] + ":" + server['portnumber'] + server['path'], auth=(server['username'], server['password']), json=requestPayload, verify=server['certificate'])
				responsePayload = json.JSONDecoder().decode(response.text)
		# toDo: use an ORM
		elif server['protocol'] == 'mysql':
			columns = ""
			values = ""
			for columnName, value in measurementData.iteritems():
				columns += ", `" + columnName + "`"
				values += ", " + value
			query = "INSERT INTO `" + hostData['type'] + hostData['modelNumber'] + "` (`isSynced`, `timestmp`" + columns + ") VALUES (False, '" + requestPayload['t'] + "'" + values + ");"
			connectionHandle = MySQLdb.connect(server['hostname'], server['username'], server['password'], server['databasename'])
			connectionCursor = connectionHandle.cursor()
			connectionCursor.execute(query)
			connectionHandle.commit()
			connectionHandle.close()
