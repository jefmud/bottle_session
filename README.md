# bottle_session
A simple session module for the Bottle framework

Session object class
    __init__(params) - creates a session object

params:
```
 secret - required secret for encrypting data
 sessions_dir - the directory to store the sessions in (defaults to './sessions')
 mode - the mode of the session storage, 'memory' or 'file' (defaults to 'memory')
 days - the number of days to keep the session in memory (defaults to 30)
```

## Example usage -- using session

at the top of your app.py file include the line
    
 ```
include bottle_session
session = bottle_session.Session('your-secret')
```
    
in each view function, include similar code that connects, 
    
```
@app.route('/somefunc')
def some_func():
    session.connect() # connect the session
    # manipulate the session data (data is the magic part of the session)
    session.data['user'] = 'joe'
    session.data['age'] = '30'
    # note that when 'file' mode is used
    # it is not saved until session.save() is called
    # and is optional (inert) if you are using 'memory' mode
    session.save()
    ...
```
