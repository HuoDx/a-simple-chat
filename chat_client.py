import socketio

sio = socketio.Client()


full_chat = []

def refresh():
    import os
    global full_chat
    
    os.system('cls')
    print('\n'.join(full_chat))
    print('/> ')
    
@sio.event
def connect():
    print('connection established')
    uname = input('Nickname: ')
    room = input('Chat room (leave empty to join the public channel): ')
    sio.emit('register-client', {
        'username': uname,
        'room': room
    })

@sio.on('ack-chat-msg')
def response(data):
    global full_chat
    full_chat.append(data)
    refresh()

@sio.on('refresh')
def r(data):
    global full_chat
    full_chat = [el for el in data]
    refresh()
    
@sio.on('chat-ready')
def my_message(data):
    global full_chat
    full_chat = [el for el in data] # load chat history
    refresh()
    print('[Server] Your chat is ready; begin chatting now.')
    msg = ''
    while True:
        msg = input('/> ')
        if(msg == '/quit'):
            break
        sio.emit('chat-message', msg)

@sio.event
def disconnect():
    print('disconnected from server')
    
try:
    addr = 'http://%s:%s'%(input('server ip: '), input('server port: '))
    print(addr)
    sio.connect(addr)
except Exception as e:
    print(e)
    exit()


