# Forks processes to retrieve parameter values through shell commands
import os
# Handle output of executing python commands stored as strings in the dictionary
import sys
# Handle output of executing python commands stored as strings in the dictionary
import StringIO
# Handle output of executing python commands stored as strings in the dictionary
import contextlib
# Retrieves the IP address
import netifaces as ni

# Handle output of executing python commands stored as strings in the dictionary
@contextlib.contextmanager
def stdoutIO(stdout=None):
	old = sys.stdout
	if stdout is None:
		stdout = StringIO.StringIO()
	sys.stdout = stdout
	yield stdout
	sys.stdout = old

# A dictionary of parameter names against their shell command names
commandsDictionarySh = {
	# Temperature of the GPU, Raspberry Pi-specific
	'temperature_gpu': '/opt/vc/bin/vcgencmd measure_temp | awk \'{print substr($1, 6, 4)}\'',
	# Temperature of the CPU
	'temperature_cpu': 'cat /sys/class/thermal/thermal_zone0/temp',
	# System information
	'uname': 'uname -a',
	# Build information, Raspberry Pi-specific
	'reference': 'cat /etc/rpi-issue',
	# OS information
	'release_os': 'cat /etc/os-release',
	# Processor Revision Number, Raspberry Pi-specific
	'revision_processor': 'cat /proc/cpuinfo | grep "Revision" | cut -d \' \' -f 2',
	# Processor Serial Number, Raspberry Pi-specific
	'serialnumber_processor': 'cat /proc/cpuinfo | grep "Serial" | cut -d \' \' -f 2',
	'hostname': 'echo $HOSTNAME',
	'username': 'whoami',
	'date': 'date'
}

# A dictionary of parameter names against their python command names
commandsDictionaryPy = {
	# IPv4 address of the 'eth0' adapter
	'ipv4_eth0': 'ni.ifaddresses(\'eth0\')[2][0][\'addr\']',
	# IPv4 address of the 'wlan0' adapter
	'ipv4_wlan0': 'ni.ifaddresses(\'wlan0\')[2][0][\'addr\']'
}

# A dictionary of formatting elements for different types of response formats
styleguide = {
	'header': {
		'html': '<html>\n<body>\n<table>\n<tbody>\n'
	},
	'simpleheader': {
		'html': '<html>\n<body>\n'
	},
	'entryLeft': {
		'html': '\t<tr>\n\t\t<td id=\"'
	},
	'entryMid': {
		'html': '\">'
	},
	'entryRight': {
		'html': '</td>\n\t</tr>\n'
	},
	'footer': {
		'html': '</tbody>\n</table>\n</body>\n</html>'
	},
	'simplefooter': {
		'html': '</body>\n</html>'
	}
}

# A wrapper function to retrieve values of parameters using either Shell or pure Python
def getParameterHandler(parameterName):
	# If the name of the requested parameter exists in the Shell dictionary, ...
	if parameterName in commandsDictionarySh.keys():
		# ... then spawn a process to retrieve that parameter's value and return the same
		return os.popen(commandsDictionarySh[parameterName]).read().strip('\n')
	# If the requested parameter's value can be computer otherwise, ...
	elif parameterName in commandsDictionaryPy.keys():
		# ... then do it
		with stdoutIO() as s:
			exec(commandsDictionaryPy[parameterName])
		return s.getvalue()
	# Or else, it's a no-go
	else:
		return ''
