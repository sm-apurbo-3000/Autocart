from website import create_app
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from flask_login import login_required, current_user
from website.admin import admin_id

app = create_app()
socketio = SocketIO(app)

# dictionary to store connected users {user_socket_id: {'user_id': 123, 'username': 'username', 'user_type': 'customer/admin', 'user_avatar': user_avatar}}
users = {}

@app.route('/customer-support/<int:user_id>') # user_id is the id of the user who is requesting support
@login_required
def customer_support(user_id):
    return render_template('customer-support.html', user_id = user_id)

# listen for connect event
@socketio.on('connect')
@login_required
def handle_connect():
    if current_user.id in admin_id:
        username = f'Admin-{current_user.username}-{current_user.id}'
        user_avatar = f'https://avatar.iran.liara.run/public/boy?username={username}'
        users[request.sid] = {'user_id': current_user.id, 'username': username, 'user_type': 'admin', 'user_avatar': user_avatar}
    else:
        username = f'Customer-{current_user.username}-{current_user.id}'
        user_avatar = f'https://avatar.iran.liara.run/public/boy?username={username}'
        users[request.sid] = {'user_id': current_user.id, 'username': username, 'user_type': 'customer', 'user_avatar': user_avatar}
    
    # https://avatar.iran.liara.run/public/boy?username=User123
    emit('user_joined', {'user_id': current_user.id, 'username': username, 'user_type': users[request.sid]['user_type'], 'user_avatar': user_avatar}, broadcast = True)
    emit('set_username', {'username': username}) # while connects first time, set username

# listen for disconnect event
@socketio.on('disconnect')
@login_required
def handle_disconnect():
    disconnected_user = users.pop(request.sid, None) # in case of undefined user, return None
    if disconnected_user:
        emit('user_left', {'user_id': disconnected_user['user_id'], 'username': disconnected_user['username'],'user_type': disconnected_user['user_type'], 'user_avatar': disconnected_user['user_avatar']}, broadcast = True)

# listen for send_message event
@socketio.on('send_message')
@login_required
def handle_send_message(data):
    sender = users.get(request.sid)
    if sender:
        emit('new_message', {'message': data['message'], 'sender_id': sender['user_id'], 'sender_username': sender['username'], 'sender_type': sender['user_type'], 'sender_avatar': sender['user_avatar']}, broadcast = True)

# listen for update_username event
@socketio.on("update_username")
@login_required
def handle_update_username(data):
    old_username = users[request.sid]["username"]
    new_username = data["username"]
    users[request.sid]["username"] = new_username

    emit("username_updated", {"old_username":old_username, "new_username":new_username}, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug = True) # default port = 5000