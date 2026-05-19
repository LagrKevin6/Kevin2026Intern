from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import datetime

app = Flask(__name__)
CORS(app)  # 允许前端跨域请求

def init_db():
    conn = sqlite3.connect('users.db')
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




@app.route('/api/register', methods=['POST'])

def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    # 【Bug 所在】此处没有校验用户名长度！
    # 需求文档要求 username 长度必须 > 5，但实际允许任意长度（包括空串）。

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