from functools import wraps
from flask import redirect, session
 
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:  # 假设使用cookie存储登录状态
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function