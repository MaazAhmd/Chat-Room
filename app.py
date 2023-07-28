from flask import Flask, request, render_template, url_for, session, redirect
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "mkphd"
socketio = SocketIO(app)

rooms = {}

def generate_code(length):
    while True:
        code = ''
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break

    return code

@app.route('/', methods=['GET', 'POST'])
def home():
    error = None
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        join = request.form.get('join', False)
        create = request.form.get('create', False)

        if not name:
            return render_template('home.html', error = "Please Enter a Name.", name=name, code=code)
        if join != False and not code:
            return render_template('home.html', error = "Please enter a code to join.", name=name, code=code)
        
        room = code
        if create != False:
            room = generate_code(4)
            print(room)
            rooms[room] = {'members': 0, 'messages': []}
        elif code not in rooms:
            return render_template('home.html', error = "Room not found.", name=name, code=code)
            
        session['name'] = name
        session['room'] = room
        return redirect(url_for('room'))

    return render_template('home.html', error=error)

@app.route('/room')
def room():
    name = session.get('name')
    room = session.get('room')
    if not name or not room or room not in rooms:
        return redirect(url_for('home'))
    
    return render_template('room.html')

@socketio.on("connect")
def connect(auth):
    name = session.get("name")
    room = session.get("room")
    if not room or not name:
        return
    elif room not in rooms:
        leave_room(room)
        return 
    
    join_room(room)
    send({"name": name, "message": " has joined the room."}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined {room}.")

@socketio.on("disconnect")
def disconnect():
    name = session.get("name")
    room = session.get("room")
    leave_room(room)
    
    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]

    send({"name": name, "message": " has left the room."}, to=room)
    print(f"{name} left {room}.")

if __name__ == "__main__":
    socketio.run(app, debug=True)