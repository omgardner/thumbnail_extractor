import json

def load_json(filepath):
	with open(filepath,'r') as jsonfile:
		return json.load(jsonfile)
	
	
def load_mime(filepath):
	mime = load_json(filepath)
	return {v:k for k,v in mime.items()} # invert dictionary


def get_extension(content_type, mime_json):
	""" mime is content_type header, uses dict lookup to find
	corresponding extension
	e.g. 'application/x-shockwave-flash': '.swf'
	"""
	try:
		# conversion from mime to ext
		return mime_json[content_type]
	except KeyError:
		return ""

def file_from_url(url):
	return url.split('/')[-1].split('?')[0]