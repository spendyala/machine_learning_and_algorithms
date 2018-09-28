import numpy
import sys
import time

from flask import Flask
from flask import request

def mm_fib(n):
    return (numpy.matrix([[2,1],[1,1]])**(n//2))[0,(n+1)%2]

app = Flask(__name__)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/ex')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

@app.route('/fib/<int:fib_number>')
def do_fib(fib_number):
    time.sleep(1)
    return f"{mm_fib(fib_number)}"

@app.route('/')
def hello():
    return "Hello World!"

if __name__ == '__main__':
    app.run()

