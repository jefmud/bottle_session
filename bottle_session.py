
"""
Simple Session for Bottle
2022 (c) Jeff Muday
MIT License, etc.
"""
import os
import pickle
import random
import string
from bottle import request, response

def _token_generator(size=12, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class Session:
    """Session object class
    __init__(params) - creates a session object

    params:
        secret - required secret for encrypting data
        sessions_dir - the directory to store the sessions in (defaults to './sessions')
        cookie_name - the name of the cookie to identify the session (defaults to 'bsession')
        mode - the mode of the session storage, 'memory' or 'file' (defaults to 'memory')
        days - the number of days to keep the session in memory (defaults to 30)

    Example usage -- using session
    at the top of your app.py file include the line
    session = Session(secret)

    in each view function, include the code or put it in @app.before_request()
    def some_func():
        session.connect()
        session.data['user'] = 'joe'
        session.data['age'] = '30'
        # note that when 'file' mode is used
        # it is not saved until session.save() is called
        # and is optional (inert) if you are using 'memory' mode
        session.save()

    """
    def __init__(self, secret, sessions_dir='./sessions', cookie_name='bsession', mode='memory', days=30):
        self._secret = secret
        self._cookie_name = cookie_name
        self._dir = sessions_dir
        self._key = None
        self.data = {} # to ensure compatibility with original version
        if mode not in ['file', 'memory']:
            raise ValueError("ERROR: Session mode must be 'file' or 'memory'")
        self._mode = mode # file, memory, or memcached (FUTURE)
        self._sessions = {}

    @property
    def session_key(self):
        """property returns a session key
        if none, then use the randomly generated one
        """
        this_session_key = request.get_cookie(self._cookie_name, None, self._secret)
        if this_session_key:
            # if there is a session key, use it
            self._key = this_session_key
        else:
            # generate a new key token
            self.new()
        return self._key

    def commit(self):
        """save the session to disk/cache, could be called after every request.
        you would also probably NOT want to call this in 'after_request', for efficiency
        """
        self._save(self.session_key)

    def save(self):
        """save the session to a file"""
        self.commit()

    def new(self):
        """
        new() - creates a new session cookie,
            purge old session (if any), blanks out the data
        """
        self.purge()
        self._key = _token_generator(32)
        self.data = {}
        response.set_cookie(self._cookie_name, self._key, self._secret)
        return self._key

    def connect(self):
        """
        connect() - connects to a session if one exists, otherwise creates a new one.
        You can call this at the top of your view function or in @app.before_request().
        """
        self._load(self.session_key)

    def _session_fname(self, session_key):
        """_session_fname() - private function to make a directory for Sessions.
        If 'file' mode and it doesn't exist and return filename,
        else if 'memory' mode, return None
        """
        if self._mode == 'file':
            os.makedirs(self._dir, exist_ok=True)
            return os.path.join(self._dir, str(session_key))
        return None

    def _load(self, session_key=None):
        """_load() - private function to load the session from disk/cache"""
        fname = self._session_fname(self.session_key)
        if session_key is None:
            # if no session key, then load the current session
            session_key = self.session_key
        if self._mode == 'file':
            if os.path.exists(fname):
                with open(fname, 'rb') as fin:
                    self.data = pickle.load(fin)
            else:
                self.data = {}
                self._save(session_key)
        elif self._mode == 'memory':
            if session_key in self._sessions:
                self.data = self._sessions[session_key]
            else:
                self._sessions[session_key] = {}
        else:
            raise Exception(f"unknown Session mode: {self._mode}")


    def _save(self, session_key=None):
        """_save() - private function to save the session to disk/cache
                returns the None
        """
        if session_key is None:
            session_key = self.session_key
        if self._mode == 'file':
            fname = self._session_fname(self.session_key)
            try:
                with open(fname, 'wb') as fout:
                    pickle.dump(self.data, fout)
            except Exception as e:
                print('ERROR: Session save failed:', e)

    def purge(self):
        """purge() - purge old session if needed"""
        if self._mode == 'file':
            if os.path.exists(self._session_fname(self.session_key)):
                os.remove(self._session_fname(self.session_key))
        elif self._mode == 'memory':
            if self._key in self._sessions:
                del self._sessions[self._key]
        self.data = {}

    def clear(self):
        """clear() - clears the session. Same as purge()"""
        self.purge()
