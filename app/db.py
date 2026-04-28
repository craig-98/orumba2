import os
import json
from functools import wraps

# Try to import supabase; if not available, fall back to JSON
try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_FILE = os.path.join(BASE_DIR, 'instance', 'posts.json')
USERS_FILE = os.path.join(BASE_DIR, 'instance', 'users.json')
EVENTS_FILE = os.path.join(BASE_DIR, 'instance', 'events.json')
ALBUMS_FILE = os.path.join(BASE_DIR, 'instance', 'albums.json')

# In-memory caches (same as original)
posts = []
users = []
events = []
albums = []

def _json_load(path, default=None):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default if default is not None else []
    return default if default is not None else []

def _json_save(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class SupabaseDB:
    """Supabase wrapper that mirrors the original JSON API exactly."""
    
    def __init__(self):
        self.client = None
        if SUPABASE_AVAILABLE:
            url = os.environ.get('SUPABASE_URL')
            key = os.environ.get('SUPABASE_KEY') or os.environ.get('SUPABASE_ANON_KEY')
            if url and key:
                self.client = create_client(url, key)
    
    def _has_client(self):
        return self.client is not None
    
    # ---------- USERS ----------
    def load_users(self):
        if not self._has_client():
            return _json_load(USERS_FILE)
        resp = self.client.table('users').select('*').execute()
        return resp.data if resp.data else []
    
    def save_user(self, user_data):
        if not self._has_client():
            data = _json_load(USERS_FILE)
            data.append(user_data)
            _json_save(USERS_FILE, data)
            return user_data
        resp = self.client.table('users').insert(user_data).execute()
        return resp.data[0] if resp.data else user_data
    
    def update_user(self, username, updates):
        if not self._has_client():
            data = _json_load(USERS_FILE)
            for u in data:
                if u.get('username') == username:
                    u.update(updates)
            _json_save(USERS_FILE, data)
            return
        self.client.table('users').update(updates).eq('username', username).execute()
    
    def get_user_by_username(self, username):
        if not self._has_client():
            data = _json_load(USERS_FILE)
            return next((u for u in data if u.get('username') == username), None)
        resp = self.client.table('users').select('*').eq('username', username).execute()
        return resp.data[0] if resp.data else None
    
    # ---------- POSTS ----------
    def load_posts(self):
        if not self._has_client():
            return _json_load(POSTS_FILE)
        resp = self.client.table('posts').select('*').execute()
        return resp.data if resp.data else []
    
    def save_post(self, post_data):
        if not self._has_client():
            data = _json_load(POSTS_FILE)
            data.append(post_data)
            _json_save(POSTS_FILE, data)
            return post_data
        resp = self.client.table('posts').insert(post_data).execute()
        return resp.data[0] if resp.data else post_data
    
    def update_post(self, post_id, updates):
        if not self._has_client():
            data = _json_load(POSTS_FILE)
            for p in data:
                if p.get('id') == post_id:
                    p.update(updates)
            _json_save(POSTS_FILE, data)
            return
        self.client.table('posts').update(updates).eq('id', post_id).execute()
    
    def delete_post(self, post_id, user_id=None):
        if not self._has_client():
            data = _json_load(POSTS_FILE)
            data = [p for p in data if not (p.get('id') == post_id and (user_id is None or p.get('user_id') == user_id))]
            _json_save(POSTS_FILE, data)
            return
        q = self.client.table('posts').delete().eq('id', post_id)
        if user_id is not None:
            q = q.eq('user_id', user_id)
        q.execute()
    
    def get_posts_by_user(self, user_id):
        if not self._has_client():
            data = _json_load(POSTS_FILE)
            return [p for p in data if p.get('user_id') == user_id]
        resp = self.client.table('posts').select('*').eq('user_id', user_id).execute()
        return resp.data if resp.data else []
    
    def get_post_by_id(self, post_id):
        if not self._has_client():
            data = _json_load(POSTS_FILE)
            return next((p for p in data if p.get('id') == post_id), None)
        resp = self.client.table('posts').select('*').eq('id', post_id).execute()
        return resp.data[0] if resp.data else None
    
    # ---------- EVENTS ----------
    def load_events(self):
        if not self._has_client():
            return _json_load(EVENTS_FILE)
        resp = self.client.table('events').select('*').execute()
        return resp.data if resp.data else []
    
    def save_event(self, event_data):
        if not self._has_client():
            data = _json_load(EVENTS_FILE)
            data.append(event_data)
            _json_save(EVENTS_FILE, data)
            return event_data
        resp = self.client.table('events').insert(event_data).execute()
        return resp.data[0] if resp.data else event_data
    
    def get_events_by_user(self, user_id):
        if not self._has_client():
            data = _json_load(EVENTS_FILE)
            return [e for e in data if e.get('user_id') == user_id]
        resp = self.client.table('events').select('*').eq('user_id', user_id).execute()
        return resp.data if resp.data else []
    
    # ---------- ALBUMS ----------
    def load_albums(self):
        if not self._has_client():
            return _json_load(ALBUMS_FILE)
        resp = self.client.table('albums').select('*').execute()
        return resp.data if resp.data else []
    
    def save_album(self, album_data):
        if not self._has_client():
            data = _json_load(ALBUMS_FILE)
            data.append(album_data)
            _json_save(ALBUMS_FILE, data)
            return album_data
        resp = self.client.table('albums').insert(album_data).execute()
        return resp.data[0] if resp.data else album_data
    
    def get_albums_by_user(self, user_id):
        if not self._has_client():
            data = _json_load(ALBUMS_FILE)
            return [a for a in data if a.get('user_id') == user_id]
        resp = self.client.table('albums').select('*').eq('user_id', user_id).execute()
        return resp.data if resp.data else []
    
    # ---------- MIGRATION / SETUP ----------
    def migrate_from_json(self):
        """One-time migration: copy all local JSON data into Supabase."""
        if not self._has_client():
            print('No Supabase client — skipping migration')
            return
        
        # Migrate users
        users_data = _json_load(USERS_FILE)
        for u in users_data:
            try:
                self.client.table('users').insert(u).execute()
            except Exception as e:
                print(f'User migrate skip (may exist): {e}')
        
        # Migrate posts
        posts_data = _json_load(POSTS_FILE)
        for p in posts_data:
            try:
                self.client.table('posts').insert(p).execute()
            except Exception as e:
                print(f'Post migrate skip: {e}')
        
        # Migrate events
        events_data = _json_load(EVENTS_FILE)
        for e in events_data:
            try:
                self.client.table('events').insert(e).execute()
            except Exception as e:
                print(f'Event migrate skip: {e}')
        
        # Migrate albums
        albums_data = _json_load(ALBUMS_FILE)
        for a in albums_data:
            try:
                self.client.table('albums').insert(a).execute()
            except Exception as e:
                print(f'Album migrate skip: {e}')
        
        print('Migration complete!')

# Global instance
db = SupabaseDB()
