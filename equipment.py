# Generate timestamps
import datetime
# Handle communications over modbus RS485/RS422/RS232
import minimalmodbus
# Handle communications over modbus TCP
from pyModbusTCP.client import ModbusClient

# Host interface for the "ABB PVS800" Central Inverter
class inverterPVS800(object):
	# The constructor for the "ABB PVS800" Central Inverter
	def __init__(self):
		super(inverterPVS800, self).__init__()
		# List of all measurements offered by the host
		self.labels = {
			1: 'currentGrid',
			2: 'powerGrid',
			3: 'frequencyGrid',
			4: 'pfGrid',
			5: 'reactivepowerGrid',
			6: 'voltagePV',
			7: 'currentPV',
			8: 'powerPV',
			9: 'temperatureInverter',
			10: 'modeInverter',
			11: 'uptimeInverter',
			12: 'electricityGeneration',
			13: 'kiloGeneration',
			14: 'megaGeneration',
			15: 'gigaGeneration',
			16: 'breakercountGrid',
			17: 'breakercountPV'
		}
		# List of register addresses for each measurement
		self.registerAddresses = {
			1: 106,
			2: 109,
			3: 111,
			4: 112,
			5: 113,
			6: 133,
			7: 117,
			8: 118,
			9: 119,
			10: 120,
			11: 124,
			12: 125,
			13: 126,
			14: 127,
			15: 128,
			16: 129,
			17: 130
		}
		# List of division factors for each measurement
		self.factors = {
			1: 1,
			2: 10,
			3: 100,
			4: 1,
			5: 1,
			6: 1,
			7: 1,
			8: 1,
			9: 1,
			10: 1,
			11: 1,
			12: 1,
			13: 1,
			14: 1,
			15: 1,
			16: 1,
			17: 1
		}
		# List of thresholds for each measurement
		self.threshold = {}
		# Space for storing modbusTCP device's file handle
		self.handle = ''
		# Space for receiving the body of a response message from the host
		self.payload = []
		# Space for storing the time stamp from the last-received response message
		self.timestmp = ''
		# Space for storing the IP address of the host
		self.IPAddress = ''
		# Flag indicating the validity of the measurement
		self.sanity = -1
	# A handler function to populate the URL of the host
	def attach(self, identity):
		self.threshold = identity['threshold']
		self.IPAddress = identity['IPAddress']
		self.handle = ModbusClient(host=self.IPAddress, auto_open=True)
	# A handler function to restore default settings
	def detach(self):
		self.payload = []
		self.timestmp = ''
		self.IPAddress = ''
		self.handle = ''
		self.sanity = -1
	# A method to retrieve measurements from the host
	def measure(self):
		self.timestmp = str(datetime.datetime.now())
		for index in range(0, len(self.labels)):
			registerData = float(self.handle.read_holding_registers(self.registerAddresses[index + 1], 1)[0]) / float(self.factors[index + 1])
			self.payload.append(str(registerData))
		self.sanity = 0
	# A method to indicate useless measurements
	def filter(self):
		# For each measurement offered by the host,...
		for index in range(0, len(self.labels)):
			# Attempt to retrieve a threshold on the value of the measurement ...
			try:
				threshold = self.threshold[self.labels[index + 1]]
			#  ... unless it doesn't exist ...
			except KeyError:
				# ... in which case, move on to the next measurement ...
				pass
			else:
				# ... or otherwise, identify the type of filter, and check if the value of the measurement complies ...
				if threshold['type'] == 'max':
					if float(self.payload[index]) > float(threshold['value']):
						return -1
				if threshold['type'] == 'min':
					if float(self.payload[index]) < float(threshold['value']):
						return -1
				if threshold['type'] == 'pass':
					if float(self.payload[index]) >= float(threshold['valueMax']):
						return -1
					if float(self.payload[index]) <= float(threshold['valueMin']):
						return -1
		# ... if all comply, indicate so
		return 0
	# A method to parse response messages from the host and serve measurement values to the caller
	def read(self, measurementIndex):
		# Unless the existing measurement is valid, do not use it
		if self.sanity != 0:
			self.measure()
		# Unless the existing measurement is valuable, do not use it
		self.sanity = self.filter()
		return self.payload[measurementIndex - 1]
	# Cancel the validity of the existing measurement
	def cancel(self):
		self.payload = []
		self.sanity = -1

# Host interface for the "Statcon Energiaa SMB-096" Combiner
class combinerSMB096(object):
	# The constructor for the "Statcon Energiaa SMB-096" Combiner interface
	def __init__(self):
		super(combinerSMB096, self).__init__()
		# List of all measurements offered by the host
		self.labels = {
			1: 'current1',
			2: 'current2',
			3: 'current3',
			4: 'current4',
			5: 'current5',
			6: 'current6',
			7: 'current7',
			8: 'current8',
			9: 'current9',
			10: 'current10',
			11: 'current11',
			12: 'current12',
			13: 'voltage_DC',
			14: 'status_spd',
			15: 'status_switch',
			16: 'temperature_scb'
		}
		# List of division factors for each measurement
		self.factors = {
			1: 100,
			2: 100,
			3: 100,
			4: 100,
			5: 100,
			6: 100,
			7: 100,
			8: 100,
			9: 100,
			10: 100,
			11: 100,
			12: 100,
			13: 1,
			14: 1,
			15: 1,
			16: 10
		}
		# List of thresholds for each measurement
		self.threshold = {}
		# Space for storing TTY device's file handle
		self.handle = ''
		# Space for receiving the body of a response message from the host
		self.payload = []
		# Space for storing the time stamp from the last-received response message
		self.timestmp = ''
		# Space for storing the port name of the host
		self.portName = ''
		# Space for storing the baudrate of the connection
		self.baudrate = 0
		# Space for storing the slave address of the host
		self.slaveAddress = 0
		# Flag indicating the validity of the measurement
		self.sanity = -1
	# A handler function to populate the URL of the host
	def attach(self, identity):
		self.threshold = identity['threshold']
		self.portName = identity['portName']
		self.baudrate = identity['baudrate']
		self.slaveAddress = int(identity['slaveAddress'])
		minimalmodbus.BAUDRATE = int(self.baudrate)
		self.handle = minimalmodbus.Instrument(self.portName, self.slaveAddress)
	# A handler function to restore default settings
	def detach(self):
		self.payload = []
		self.timestmp = ''
		self.portName = ''
		self.baudrate = 0
		self.slaveAddress = 0
		self.handle = ''
		self.sanity = -1
	# A method to retrieve measurements from the host
	def measure(self):
		self.timestmp = str(datetime.datetime.now())
		for index in range(0, len(self.labels)):
			registerAddress = index
			registerData = float(self.handle.read_register(registerAddress, functioncode = 3)) / float(self.factors[index + 1])
			self.payload.append(str(registerData))
		self.sanity = 0
	# A method to indicate useless measurements
	def filter(self):
		# For each measurement offered by the host,...
		for index in range(0, len(self.labels)):
			# Attempt to retrieve a threshold on the value of the measurement ...
			try:
				threshold = self.threshold[self.labels[index + 1]]
			#  ... unless it doesn't exist ...
			except KeyError:
				# ... in which case, move on to the next measurement ...
				pass
			else:
				# ... or otherwise, identify the type of filter, and check if the value of the measurement complies ...
				if threshold['type'] == 'max':
					if float(self.payload[index]) >= float(threshold['value']):
						return -1
				if threshold['type'] == 'min':
					if float(self.payload[index]) <= float(threshold['value']):
						return -1
				if threshold['type'] == 'pass':
					if float(self.payload[index]) >= float(threshold['valueMax']):
						return -1
					if float(self.payload[index]) <= float(threshold['valueMin']):
						return -1
		# ... if all comply, indicate so
		return 0
	# A method to parse response messages from the host and serve measurement values to the caller
	def read(self, measurementIndex):
		# Unless the existing measurement is valid, do not use it
		if self.sanity != 0:
			self.measure()
		# Unless the existing measurement is valuable, do not use it
		self.sanity = self.filter()
		return self.payload[measurementIndex - 1]
	# Cancel the validity of the existing measurement
	def cancel(self):
		self.payload = []
		self.sanity = -1

# Host interface for the "SMA Sunny Web Box" Logger
class loggerSunnyWebBox(object):
	# The constructor for the "SMA Sunny Web Box" Logger interface
	def __init__(self):
		super(loggerSunnyWebBox, self).__init__()
		# List of all measurements offered by the host
		self.labels = {
			0: 'power_D',
			1: 'energyToday_D',
			2: 'energyCumulative_D'
		}
		# Space for receiving the body of a response message from the host
		self.payload = []
		# Space for storing the time stamp from the last-received response message
		self.timestmp = ''
		# Space for storing the URL of the host
		self.address = ''
		# Flag indicating the validity of the measurement
		self.sanity = -1
	# A handler function to populate the URL of the host
	def attach(self, identity):
		self.address = identity['address']
	# A handler function to restore default settings
	def detach(self):
		self.payload = []
		self.timestmp = ''
		self.address = ''
		self.sanity = -1
	# A method to retrieve measurements from the host
	def measure(self):
		self.timestmp = str(datetime.datetime.now())
		# try ... except here
		text = requests.get(self.address + 'home.htm?saltpepper=' + self.timestmp).text
		subtext = text
		subtext = subtext[subtext.find('Power\"'):]
		subtext = subtext[subtext.find('>') + 1:]
		if subtext[subtext.find(' ') + 1:subtext.find('<')] == 'kW':
			self.payload.append(str(float(subtext[:subtext.find(' ')]) * 1000.0))
		elif subtext[subtext.find(' ') + 1:subtext.find('<')] == 'W':
			self.payload.append(str(float(subtext[:subtext.find(' ')])))
		subtext = subtext[subtext.find('DailyYield\"'):]
		subtext = subtext[subtext.find('>') + 1:]
		if subtext[subtext.find(' ') + 1:subtext.find('<')] == 'kWh':
			self.payload.append(str(float(subtext[:subtext.find(' ')])))
		elif subtext[subtext.find(' ') + 1:subtext.find('<')] == 'Wh':
			self.payload.append(str(float(subtext[:subtext.find(' ')]) / 1000.0))
		elif subtext[subtext.find(' ') + 1:subtext.find('<')] == 'MWh':
			self.payload.append(str(float(subtext[:subtext.find(' ')]) * 1000.0))
		subtext = subtext[subtext.find('TotalYield\"'):]
		subtext = subtext[subtext.find('>') + 1:]
		if subtext[subtext.find(' ') + 1:subtext.find('<')] == 'MWh':
			self.payload.append(str(float(subtext[:subtext.find(' ')]) / 1000.0))
		elif subtext[subtext.find(' ') + 1:subtext.find('<')] == 'GWh':
			self.payload.append(str(float(subtext[:subtext.find(' ')])))
		self.sanity = 0
	# A method to parse response messages from the host and serve measurement values to the caller
	def read(self, measurementIndex):
		# Unless the existing measurement is valid, do not use it
		if self.sanity != 0:
			self.measure()
		return self.payload[measurementIndex]
	# Cancel the validity of the existing measurement
	def cancel(self):
		self.payload = []
		self.sanity = -1
