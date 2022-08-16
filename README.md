# bottle_session
`bottle_session` is a simple session module for the Bottle framework.  Some other projects have session managers for Bottle, but I felt a very simple session was in the spirit of the Bottle framework.

The session is referenced with a simple cookie that can be stored in memory only or a pickled server-side cache.


### Caveat
Although a somewhat rare occurence, the session is **not thread safe** if two different processes are associating themselves with the same session.

Session object class
    __init__(params) - creates a session object

params:
```
 secret - required secret for encrypting data
 sessions_dir - the directory to store the sessions in (defaults to './sessions')
 cookie_name - the name of the cookie to reference the session (defaults to 'bsession')
 mode - 'memory', 'file' (defaults to 'memory')
 days - the number of days to keep the session in memory (defaults to 30)
```

## Example usage -- using session

at the top of your app.py file include the line
    
 ```
include bottle_session
session = bottle_session.Session('your-secret')
```
    
in each view function, include similar code that connects, and keeps the session data organize with the dictionary `session.data`.
    
```
@app.route('/somefunc')
def some_func():
    session.connect() # connect the session
    # manipulate the session.data dictionary
    session.data['user'] = 'joe'
    session.data['age'] = '30'
    # note that when 'file' mode is used
    # it is not saved until session.save() is called
    # and is optional (inert) if you are using 'memory' mode
    session.save()
    ...
```

Alternately you could put a session connect in the `before_request` and save the session in the `after_request`.  Though it is somewhat inefficient to do this.

```
@app.before_request
def before_request():
    session.connect()
    
@app.after_request
def after_request():
    session.save()
```

Then when the user's session is done, you can purge or clear the session with `session.purge()` or `session.clear()` both are equivalent.

```
@app.route('/logout')
def logout():
    session.purge()
```

# Acknowlegements
Thanks to Marcel Helkamp and the Bottle community for developing the Bottle Framework.
