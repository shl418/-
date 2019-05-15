import re

def index():
	with open("./templates/index.html","r") as f:
		content = f.read()

	my_stock_info = "mysql data"
	content = re.sub(r"\{%content%\}",my_stock_info,content)
	return content

def center():
	with open("./templates/center.html","r") as f:
		content = f.read()

	my_stock_info = "mysql data"
	content = re.sub(r"\{%content%\}",my_stock_info,content)
	return content

def application(env, start_response):
	print("into application")
	start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
	print("set_header")
	file_name = env['PATH_INFO']
	print(file_name)
	if file_name == "center.py":
		return center()
	elif file_name == "index.py":
		return index()
	else:
		return '我爱你中国'

