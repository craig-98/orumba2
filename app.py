from flask import Flask, send_from_directory, request, jsonify, send_file, session, redirect, url_for, render_template
import os
import json
import hashlib
import secrets
from functools import wraps

from app.db import db

app = Flask(__name__, static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), 'static')), static_url_path='/static', template_folder='app/templates')
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(24)

posts = []
users = []
events = []
albums = []

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.static_folder, 'images'), 'orumba-north-logo.jpg', mimetype='image/jpeg')

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt', mimetype='text/plain')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_posts():
    global posts
    loaded = db.load_posts()
    for p in loaded:
        if 'user_id' not in p:
            p['user_id'] = None
        if 'category' not in p:
            p['category'] = 'general'
        if 'status' not in p:
            p['status'] = 'published' if p.get('author') else 'draft'
        if 'image' not in p:
            p['image'] = ''
    posts = loaded

def save_posts():
    pass

def load_users():
    global users
    loaded = db.load_users()
    next_user_id = 1
    for user in loaded:
        if 'id' not in user:
            user['id'] = next_user_id
            next_user_id += 1
        if 'role' not in user:
            user['role'] = 'citizen'
        if 'name' not in user:
            user['name'] = user['username']
        if 'email' not in user:
            user['email'] = ''
        if 'avatar' not in user:
            user['avatar'] = ''
    users = loaded

def save_users():
    pass

def load_events():
    global events
    events = db.load_events()

def save_events():
    pass

def load_albums():
    global albums
    loaded = db.load_albums()
    for alb in loaded:
        if 'user_id' not in alb:
            alb['user_id'] = None
    albums = loaded

def save_albums():
    pass

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect('/login')
        current_user = next((u for u in users if u['username'] == session['username']), None)
        if not current_user:
            session.pop('username', None)
            return redirect('/login')
        if 'id' not in current_user:
            current_user['id'] = 1
        if 'role' not in current_user:
            current_user['role'] = 'citizen'
        session['user_id'] = current_user['id']
        session['role'] = current_user['role']
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        login_required(lambda: None)(*args, **kwargs)
        if session.get('role') != 'admin':
            return jsonify({'status': 'error', 'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    username = session.get('username')
    return next((u for u in users if u['username'] == username), None) if username else None

# Profile routes
@app.route('/profile')
@app.route('/profile/<section>')
@login_required
def profile(section='dashboard'):
    return render_template('profile/profile.html', section=section)

@app.route('/api/profile/stats', methods=['GET'])
@login_required
def api_profile_stats():
    user_id = session.get('user_id')
    post_count = len([p for p in posts if p.get('user_id') == user_id])
    album_count = len([a for a in albums if a.get('user_id') == user_id])
    event_count = len([e for e in events if e.get('user_id') == user_id])
    return jsonify({
        'status': 'success',
        'stats': {'posts': post_count, 'albums': album_count, 'events': event_count}
    })

@app.route('/api/profile/posts', methods=['GET'])
@login_required
def api_profile_posts():
    user_id = session.get('user_id')
    user_posts = [p for p in posts if p.get('user_id') == user_id]
    return jsonify({'status': 'success', 'posts': user_posts})

@app.route('/api/profile/posts', methods=['POST'])
@login_required
def api_create_post():
    data = request.get_json()
    user_id = session.get('user_id')
    max_id = max([p.get('id', 0) for p in posts], default=0)
    new_post = {
        'id': max_id + 1,
        'user_id': user_id,
        'title': data.get('title', ''),
        'content': data.get('content', ''),
        'category': data.get('category', 'general'),
        'image': data.get('image', ''),
        'status': data.get('status', 'draft'),
        'created_at': data.get('created_at', '')
    }
    db.save_post(new_post)
    posts.append(new_post)
    return jsonify({'status': 'success', 'post': new_post})

@app.route('/api/profile/posts/<int:post_id>', methods=['PUT'])
@login_required
def api_update_post(post_id):
    user_id = session.get('user_id')
    post = next((p for p in posts if p['id'] == post_id and p.get('user_id') == user_id), None)
    if not post:
        return jsonify({'status': 'error', 'message': 'Post not found'}), 404
    data = request.get_json()
    post.update(data)
    db.update_post(post_id, data)
    return jsonify({'status': 'success', 'post': post})

@app.route('/api/profile/posts/<int:post_id>', methods=['DELETE'])
@login_required
def api_delete_post(post_id):
    user_id = session.get('user_id')
    global posts
    posts = [p for p in posts if not (p['id'] == post_id and p.get('user_id') == user_id)]
    db.delete_post(post_id, user_id)
    return jsonify({'status': 'success'})

@app.route('/api/profile/albums', methods=['GET'])
@login_required
def api_profile_albums():
    user_id = session.get('user_id')
    user_albums = [a for a in albums if a.get('user_id') == user_id]
    return jsonify({'status': 'success', 'albums': user_albums})

@app.route('/api/profile/albums', methods=['POST'])
@login_required
def api_create_album():
    data = request.get_json()
    user_id = session.get('user_id')
    max_id = max([a.get('id', 0) for a in albums], default=0)
    new_album = {
        'id': max_id + 1,
        'user_id': user_id,
        'title': data.get('title', ''),
        'posts': data.get('posts', [])
    }
    db.save_album(new_album)
    albums.append(new_album)
    return jsonify({'status': 'success', 'album': new_album})

@app.route('/api/profile/events', methods=['GET'])
@login_required
def api_profile_events():
    user_id = session.get('user_id')
    user_events = [e for e in events if e.get('user_id') == user_id]
    return jsonify({'status': 'success', 'events': user_events})

@app.route('/api/profile/events', methods=['POST'])
@login_required
def api_create_event():
    data = request.get_json()
    user_id = session.get('user_id')
    max_id = max([e.get('id', 0) for e in events], default=0)
    new_event = {
        'id': max_id + 1,
        'user_id': user_id,
        **data
    }
    db.save_event(new_event)
    events.append(new_event)
    return jsonify({'status': 'success', 'event': new_event})

@app.route('/api/upload/image', methods=['POST'])
@login_required
def api_upload_image():
    if 'file' not in request.files:
        return jsonify({'status': 'error'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error'}), 400
    user_id = session.get('user_id')
    upload_dir = os.path.join('static', 'uploads', 'user_' + str(user_id))
    os.makedirs(os.path.join(BASE_DIR, upload_dir), exist_ok=True)
    filename = hashlib.md5(file.filename.encode()).hexdigest() + '_' + file.filename
    filepath = os.path.join(BASE_DIR, upload_dir, filename)
    file.save(filepath)
    url = '/' + upload_dir.replace('\\', '/') + '/' + filename
    return jsonify({'status': 'success', 'url': url})

@app.route('/api/profile/settings', methods=['PUT'])
@login_required
def api_update_profile():
    data = request.get_json()
    username = session['username']
    user = next(u for u in users if u['username'] == username)
    allowed = ['name', 'email', 'avatar']
    for key in allowed:
        if key in data:
            user[key] = data[key]
    db.update_user(username, {k: v for k, v in data.items() if k in allowed})
    return jsonify({'status': 'success'})

# Load initial data
load_users()
load_posts()
load_albums()
load_events()

@app.route('/')
def serve_home():
    return render_template('home.html')

@app.route('/login', methods=['GET'])
def serve_login():
    return render_template('login.html')

@app.route('/register', methods=['GET'])
def serve_register():
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('serve_home'))

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Username and password are required'}), 400
    if any(u['username'] == username for u in users):
        return jsonify({'status': 'error', 'message': 'Username already exists'}), 400
    hashed_pw = hash_password(password)
    new_user = {
        'username': username,
        'password': hashed_pw,
        'id': max([u.get('id', 0) for u in users], default=0) + 1,
        'role': 'citizen',
        'name': username,
        'email': '',
        'avatar': ''
    }
    db.save_user(new_user)
    users.append(new_user)
    return jsonify({'status': 'success', 'message': 'User registered successfully'})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Username and password are required'}), 400
    user = next((u for u in users if u['username'] == username), None)
    if user and user['password'] == hash_password(password):
        session['username'] = username
        return jsonify({'status': 'success', 'message': 'Logged in successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('username', None)
    return jsonify({'status': 'success', 'message': 'Logged out successfully'})

@app.route('/api/check-auth', methods=['GET'])
def api_check_auth():
    if 'username' in session:
        return jsonify({'status': 'success', 'authenticated': True, 'username': session['username']})
    else:
        return jsonify({'status': 'success', 'authenticated': False})

@app.route('/create-post')
@login_required
def serve_create_post():
    return render_template('create_post.html')

@app.route('/create-album')
@login_required
def serve_create_album():
    return render_template('create_album.html')

@app.route('/create-event')
@login_required
def serve_create_event():
    return render_template('create_event.html')

@app.route('/api/public/posts', methods=['GET'])
def api_public_get_posts():
    public_posts = [p for p in posts if p.get('status') == 'published']
    return jsonify({'status': 'success', 'posts': public_posts})

@app.route('/api/public/events', methods=['GET'])
def api_public_get_events():
    public_events = [e for e in events if e.get('status') == 'published']
    return jsonify({'status': 'success', 'events': public_events})

@app.route('/api/public/post/<int:post_id>', methods=['GET'])
def api_get_post(post_id):
    post = next((p for p in posts if p.get('id') == post_id), None)
    if post:
        return jsonify({
            'status': 'success',
            'post': {
                'id': post.get('id'),
                'title': post.get('title', 'Untitled'),
                'content': post.get('content'),
                'username': post.get('author'),
                'published_at': post.get('published_at', '2024-01-01T00:00:00Z')
            }
        })
    return jsonify({'status': 'error', 'message': 'Post not found'}), 404

@app.route('/api/public/albums', methods=['GET'])
def api_public_get_albums():
    return jsonify({'status': 'success', 'albums': albums})

@app.route('/about')
def serve_about():
    return render_template('about.html')

@app.route('/services')
def serve_services():
    return render_template('services.html')

@app.route('/members')
def serve_members():
    return render_template('members.html')

@app.route('/government')
def serve_government():
    return render_template('government.html')

@app.route('/government/administration')
def serve_administration():
    return render_template('government/administration.html')

@app.route('/government/management-team')
def serve_management_team():
    return render_template('government/management-team.html')

@app.route('/chairman-leadership')
def serve_chairman():
    return render_template('chairman-leadership.html')

@app.route('/procedure-by-laws')
def serve_procedure():
    return render_template('government.html')

@app.route('/map-explore')
def serve_map():
    return render_template('map-explore.html')

@app.route('/contact')
def serve_contact():
    return render_template('contact.html')

@app.route('/about/history')
def serve_history():
    return render_template('about/history.html')

@app.route('/about/landmarks-culture')
def serve_culture():
    return render_template('about/landmarks-culture.html')

@app.route('/about/people')
def serve_people():
    return render_template('about/people.html')

@app.route('/news-announcements')
def serve_news():
    return render_template('news-announcements.html')

@app.route('/gallery')
def serve_gallery():
    return render_template('gallery.html')

@app.route('/newsroom')
def serve_newsroom():
    return render_template('newsroom.html')

@app.route('/upcoming-events')
def serve_upcoming_events():
    return render_template('upcoming-events.html')

@app.route('/post/<int:post_id>')
def serve_post(post_id):
    return render_template('post.html')

@app.route('/departments')
def serve_departments():
    return render_template('departments.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
