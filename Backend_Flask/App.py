from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import hashlib
import datetime

#app = Flask(__name__)
app = Flask(__name__, static_folder='../Frontend_ReAct', static_url_path='')

CORS(app)  # 允许前端跨域请求


# 添加一个路由来提供 index.html
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

#提供 admin.html
@app.route('/admin')
def serve_admin():
    return send_from_directory(app.static_folder, 'admin.html')

def init_db():
    conn = sqlite3.connect('users.db') #SQLite,如有需要换其他SQL
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    return sqlite3.connect('users.db')




#注册
@app.route('/api/register', methods=['POST'])

def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    # 预设bug:不限制用户名长度，然后到时候在测试的prd里面写一下，用户名的长度必须大于x位

    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                  (username, hash_password(password)))
        conn.commit()
        return jsonify({'success': True, 'message': '注册成功'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
    finally:
        conn.close()


#登录
@app.route('/api/login', methods=['POST'])

def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()

    if row and row[0] == hash_password(password):
        return jsonify({'success': True, 'message': '登录成功'})
    else:
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401





# （以下为管理员功能）查询所有用户
@app.route('/api/users', methods=['GET'])
def get_all_users():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT username FROM users ORDER BY username')
    users = [{'username': row[0]} for row in c.fetchall()]
    conn.close()
    return jsonify({'success': True, 'users': users})

#  删除用户
@app.route('/api/users/<username>', methods=['DELETE'])
def delete_user(username):
    # 可选：增加管理员校验（这里简化，直接允许删除）
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE username = ?', (username,))
    if c.rowcount == 0:
        conn.close()
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': f'用户 {username} 已删除'})

#  修改密码
@app.route('/api/users/<username>', methods=['PUT'])
def update_password(username):
    data = request.get_json()
    new_password = data.get('new_password', '')
    
    if not new_password:
        return jsonify({'success': False, 'message': '新密码不能为空'}), 400
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE users SET password = ? WHERE username = ?',
              (hash_password(new_password), username))
    
    if c.rowcount == 0:
        conn.close()
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': f'用户 {username} 密码已更新'})

#  批量删除（可选，清空所有用户）
@app.route('/api/users', methods=['DELETE'])
def delete_all_users():
    # 危险操作，建议加校验
    confirm = request.args.get('confirm', 'false')
    if confirm != 'true':
        return jsonify({'success': False, 'message': '需要确认参数 ?confirm=true'}), 400
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM users')
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': '所有用户已删除'})

#  查询单个用户信息
@app.route('/api/users/<username>', methods=['GET'])
def get_user(username):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT username FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return jsonify({'success': True, 'user': {'username': row[0]}})
    else:
        return jsonify({'success': False, 'message': '用户不存在'}), 404




#报时测试链接
nowTime = datetime.datetime.now()

@app.route('/time')
def get_time():
    return {
        'Task': '''前后端链接成功
        Connect the frontend and the backend successfully!''',
        'Date': nowTime,
        'Frontend': 'React',
        'Backend': 'Flask'
    }


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)