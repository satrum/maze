#pip install bottle
#python C:\WORK\Docs\python\geekbrains\project5-git\test\hello_bottle.py
#browser: http://localhost:8080/hello/roman
'''example:
Bottle v0.12.13 server starting up (using WSGIRefServer())...
Listening on http://localhost:8080/
Hit Ctrl-C to quit.

127.0.0.1 - - [22/Mar/2017 14:19:32] "GET /hello/roman HTTP/1.1" 200 19
'''

from bottle import route, run, template

@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)

run(host='localhost', port=8080)

