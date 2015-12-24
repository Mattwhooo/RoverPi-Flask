from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit

app = Flask(__name__)
io = SocketIO(app)

@app.route('/')
def hello_world():
    return render_template('index.jade', title = 'SomeTitle')


@io.on('connect')
def ws_conn():
    print('hello connect')
    io.emit('msg', 'hello world')

@io.on('gamepadUpdate')
def update_gamepad(data):
    print(data)

if __name__ == '__main__':
    app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

    io.run(app)