from aiohttp import web
import socketio

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

async def index(request):
    """Serve the client-side application."""
    return web.json_response({
        'kidding': True
    })

@sio.event
def connect(sid, environ):
    print("connect ", sid)

users = {}

class Room:
    
    def __init__(self):
        self._history = []
    def append_message(self, msg: str):
        self._history.append(msg)
    
    def get_history(self):
        return self._history

rooms = {}

class ChatClient:
    def __init__(self, sid, room_id, username):
        self.sid = sid
        self.room_id = room_id
        self.username = username

PUBLIC_ROOM = 'public'
DEFAULT_USERNAME = 'user'

@sio.on('register-client')
async def register(sid, data):
    global users
    
    room = data.get('room', PUBLIC_ROOM)
    if room == '':
        room = PUBLIC_ROOM
    username = data.get('username', 'user')
    if username == '':
        username = DEFAULT_USERNAME
        
    users.update({
        sid: ChatClient(
            sid,
            room,
            username
        )
    })
    sio.enter_room(sid, room)
    if room not in rooms:
        rooms.update({
            room: Room()
        })
    
    print('New user [%s] in room <%s>'%(username, room))
    rooms.get(room).append_message('[User "%s" joined the room]'%username)
    await sio.emit('chat-ready', rooms.get(room).get_history(), to=sid)
    await sio.emit('refresh', rooms.get(room).get_history(), room=room)
    
@sio.on('chat-message')
async def chat_message(sid, data):
    global users
    user = users.get(sid)
    message = '[%s] %s' % (user.username, data)
    rooms.get(user.room_id).append_message(message)
    
    await sio.emit('ack-chat-msg', message, room=user.room_id)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)
    user = users.get(sid)
    if user is not None:
        sio.leave_room(sid, user.room_id)
        del(users[sid])
        rooms.get(user.room_id).append_message('[User "%s" left the room]'%user.username)
        sio.emit('ack-chat-msg', '[User "%s" left the room]'%user.username, room=user.room_id)

app.router.add_get('/', index)

if __name__ == '__main__':
    web.run_app(app, port=5000)