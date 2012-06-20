import json
import httplib
import pprint as pp

# json headers for gentoostats-cli
headers = {'Accept': 'application/json'}

def GET(server, url, headers, https=True):
	"""
	Get url from server using headers
	"""
	if https:
		conn = httplib.HTTPSConnection(server)
	else:
		conn = httplib.HTTPConnection(server)
	try:
		conn.request('GET', url=url, headers=headers)
		data = conn.getresponse().read()
	except httplib.HTTPException:
		return None
	finally:
		if conn:
			conn.close()

	return data

def deserialize(obj):
	"""
	Decode json object
	"""
	try:
		return json.JSONDecoder().decode(obj)
	except (ValueError, TypeError):
		return None

def pprint(title, obj):
	"""
	Pretty printer for the decoded json data
	"""
	print(title)
	pp.pprint(obj)
