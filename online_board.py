from flask import Flask, request, jsonify, render_template_string
import sqlite3
import datetime
import hashlib
import os
import threading

app = Flask(__name__)
DB_FILE = "online_board.db"

# HTML шаблоны
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Анонимная Онлайн Борда</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial; margin: 20px; background: #f0f0f0; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .logo { text-align: center; font-family: monospace; background: black; color: lime; padding: 10px; }
        .topic { border: 1px solid #ccc; margin: 10px 0; padding: 15px; border-radius: 5px; }
        .topic-title { font-size: 1.2em; font-weight: bold; color: #333; }
        .topic-meta { color: #666; font-size: 0.9em; }
        .topic-content { margin: 10px 0; white-space: pre-wrap; }
        form { margin: 20px 0; }
        input, textarea { width: 100%; margin: 5px 0; padding: 8px; }
        button { background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <pre>

⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣄⣤⣤⣤⣤⣤⣠⣠⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⠶⠺⢛⣉⣍⣬⣤⣤⣤⣤⣤⣤⣥⣩⣙⠛⠳⢦⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⡴⠟⣉⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣤⣉⠻⢦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠟⣁⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⡌⠻⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣴⠟⣡⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⢿⢿⡻⠛⣋⡋⠛⢻⢿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠻⢦⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣠⡟⣠⣾⣿⡿⠟⢉⣾⣿⣿⡿⣻⢝⣮⢯⣺⣮⢀⡱⣕⠀⢀⢯⣳⣳⣝⢟⣿⣿⣿⣦⠉⠻⣿⣿⣷⡌⢳⣄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣴⠏⣰⣿⠋⡵⠁⣠⣿⣿⢿⢝⣮⣿⣿⢯⣳⣿⣿⣿⡯⢂⣠⣾⣿⣪⢿⣿⣿⣼⡺⣻⣿⡷⣄⠈⢮⠹⣿⣆⠹⣆⠀⠀⠀⠀
⠀⠀⠀⣼⠃⣼⢿⠁⢨⡥⠚⣡⣿⢏⣷⣿⣿⣿⡯⣳⣿⣿⣿⣿⣏⢾⣿⣿⣿⣷⡫⣿⣿⣿⣿⣵⢻⢿⡌⠲⢼⡀⢸⢻⣧⠸⣇⠀⠀⠀
⠀⠀⢰⠏⣸⡏⢸⡀⠍⣠⢼⡿⣕⣯⣞⣮⣳⣳⢝⣵⣳⣳⣳⣵⠁⠁⣷⣝⣮⣷⣝⡞⣮⣞⣞⣮⣯⡫⣿⡖⣄⠁⢰⡃⢹⣆⠹⡆⠀⠀
⠀⢀⡿⢰⣿⠀⢸⣠⠞⢡⣿⡫⣾⣿⣿⣿⣿⢯⣫⣿⣿⣿⣿⡿⠣⠚⢿⢿⣿⣿⣿⢮⢿⣿⣿⣿⣿⣯⡺⣿⡈⠳⣸⠀⢘⣿⡆⣻⠀⠀
⠀⢸⡇⣺⡟⡅⠐⠅⢠⣾⡷⣽⣿⣿⣿⣿⣿⡳⡻⠟⠟⠋⢰⣿⡇⡸⣿⡇⠉⠻⠻⠳⡻⣿⣿⣿⣿⣿⣞⢽⣷⡄⠘⠀⣸⢹⣧⢸⡇⠀
⠀⣽⠂⣿⠅⢷⡈⣰⢋⣾⢯⣺⢿⢿⢿⢿⢟⠂⠀⠀⠀⠀⢸⣿⣏⢺⣿⡇⠀⠀⠀⠀⠨⢿⢿⢿⢿⢿⢗⣟⣷⠙⣦⢁⡯⢘⣿⢀⣗⠀
⠀⣽⠐⣿⡇⠈⣷⠁⢰⣿⢯⣺⣷⣿⣾⣷⣯⠀⠀⠀⠀⠀⠐⣿⡇⢸⣿⠁⠀⠀⠀⠀⠀⢯⣷⣯⣷⣯⡷⣵⣿⡆⠈⡾⠁⢸⣿⠀⡷⠀
⠀⢽⠌⣿⣳⡀⠨⠀⣞⢿⣯⣺⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠘⠇⠸⠃⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⢯⣺⡯⣳⠀⠁⣠⢟⣿⢈⡯⠀
⠀⢹⡇⢽⡆⠻⣄⢸⡇⢸⣿⡼⣽⣿⣿⣿⠅⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⣿⡿⡵⣿⡇⢸⡇⣴⠋⣸⡯⢰⡇⠀
⠀⠈⣷⠘⣿⡀⠈⢳⠇⢘⡟⣷⡳⡻⡻⡽⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡻⣻⢻⣹⡾⢻⡂⢸⠚⠀⣰⣿⠃⡾⠀⠀
⠀⠀⠸⡆⢻⣟⢦⣄⠁⠐⣗⠘⢿⣝⡽⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⢯⣳⡿⠀⡿⠀⢂⣠⠞⣽⡏⣰⠏⠀⠀
⠀⠀⠀⢻⡄⢿⣦⠉⠳⢦⣹⡀⠸⡻⣾⡝⣟⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⣻⣹⡵⢟⠅⢠⡧⠖⠋⣁⣾⡟⣠⠗⠀⠀⠀
⠀⠀⠀⠀⠻⣄⠻⣿⣤⡀⠀⠓⠀⢳⡈⠛⣷⣯⡣⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣽⡾⠋⢠⠏⠠⠊⢀⣠⢶⣿⠟⣠⠏⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠹⣦⠙⢿⣮⡛⠲⠶⠦⠽⢄⢀⠛⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠋⢀⠴⠽⠔⠞⠚⣋⣼⡿⢋⡴⠃⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠻⣄⠛⣿⣶⡦⡤⣤⢤⡤⡶⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠶⡦⣤⣤⢤⢶⣾⡿⢋⢴⠞⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⣆⡙⠿⣶⣤⣁⣀⣀⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣄⣄⣤⣴⡾⡟⢋⡴⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠶⣌⡙⠻⢿⣿⣿⠅⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⣿⣿⠿⠟⣉⡴⠖⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠓⠶⢤⣍⣁⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣈⣡⡥⠖⠋⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠈⠉⠋⠋⠓⠓⠓⠋⠋⠋⠉⠁⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
            </pre>
        </div>

        <h2>📝 Создать новую тему</h2>
        <form action="/create" method="post">
            <input type="text" name="title" placeholder="Заголовок темы" required>
            <textarea name="content" placeholder="Текст сообщения" rows="6" required></textarea>
            <button type="submit">📤 Опубликовать</button>
        </form>

        <h2>📂 Все темы ({{ topics_count }})</h2>
        {% for topic in topics %}
        <div class="topic">
            <div class="topic-title">{{ topic.title }}</div>
            <div class="topic-meta">
                🔑 ID: {{ topic.id }} | 
                🕐 {{ topic.timestamp }} | 
                👤 {{ topic.author_ip }}
            </div>
            <div class="topic-content">{{ topic.content }}</div>
        </div>
        {% endfor %}

        <div style="text-align: center; margin-top: 20px; color: #666;">
            🔄 Автообновление каждые 30 сек | 
            📱 Доступно с любого устройства
        </div>
    </div>

    <script>
        // Автообновление страницы
        setTimeout(() => { location.reload(); }, 30000);
        
        // Подтверждение перед отправкой
        document.querySelector('form').addEventListener('submit', function(e) {
            if(!confirm('Отправить тему? Редактирование будет невозможно!')) {
                e.preventDefault();
            }
        });
    </script>
</body>
</html>
"""

SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Тема создана!</title>
    <meta charset="utf-8">
</head>
<body>
    <div style="text-align: center; margin-top: 100px;">
        <h1>✅ Тема успешно создана!</h1>
        <p>ID темы: <strong>{{ topic_id }}</strong></p>
        <p>🔗 Поделитесь ссылкой: <code>{{ url }}/</code></p>
        <a href="/">← Вернуться к борде</a>
    </div>
</body>
</html>
"""

def init_database():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS topics (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            author_ip TEXT DEFAULT 'unknown'
        )
    ''')
    conn.commit()
    conn.close()

def generate_id(text: str) -> str:
    """Генерация уникального ID"""
    return hashlib.md5(f"{text}{datetime.datetime.now().isoformat()}".encode()).hexdigest()[:10]

@app.route('/')
def index():
    """Главная страница"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, content, timestamp, author_ip FROM topics ORDER BY timestamp DESC')
    
    topics = []
    for row in cursor.fetchall():
        topics.append({
            'id': row[0],
            'title': row[1],
            'content': row[2],
            'timestamp': row[3],
            'author_ip': row[4]
        })
    
    conn.close()
    
    return render_template_string(MAIN_TEMPLATE, topics=topics, topics_count=len(topics))

@app.route('/create', methods=['POST'])
def create_topic():
    """Создание новой темы"""
    title = request.form['title']
    content = request.form['content']
    user_ip = request.remote_addr
    
    topic_id = generate_id(title + content)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO topics (id, title, content, timestamp, author_ip)
        VALUES (?, ?, ?, ?, ?)
    ''', (topic_id, title, content, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_ip))
    
    conn.commit()
    conn.close()
    
    return render_template_string(SUCCESS_TEMPLATE, topic_id=topic_id, url=request.host_url)

@app.route('/api/topics')
def api_topics():
    """API для получения тем (для мобильных приложений)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, content, timestamp, author_ip FROM topics ORDER BY timestamp DESC')
    
    topics = []
    for row in cursor.fetchall():
        topics.append({
            'id': row[0],
            'title': row[1],
            'content': row[2],
            'timestamp': row[3],
            'author_ip': row[4]
        })
    
    conn.close()
    return jsonify(topics)

@app.route('/api/create', methods=['POST'])
def api_create():
    """API для создания темы"""
    data = request.get_json()
    title = data['title']
    content = data['content']
    user_ip = request.remote_addr
    
    topic_id = generate_id(title + content)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO topics (id, title, content, timestamp, author_ip)
        VALUES (?, ?, ?, ?, ?)
    ''', (topic_id, title, content, datetime.datetime.now().isoformat(), user_ip))
    
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "topic_id": topic_id})

def start_server():
    """Запуск сервера"""
    init_database()
    print("🚀 Запуск онлайн борды...")
    print("🌐 Сервер будет доступен по адресу: http://localhost:5000")
    print("📱 Откройте этот адрес на любом устройстве в вашей сети")
    print("\n⚠️  Для доступа из интернета используйте:")
    print("   ngrok http 5000")
    print("   ИЛИ")
    print("   ssh -R 80:localhost:5000 nokey@localhost.run")
    print("\n⏹️  Для остановки сервера нажмите Ctrl+C")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    start_server()