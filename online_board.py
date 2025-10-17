#!/usr/bin/env python3
"""
АНОНИМНАЯ ОНЛАЙН БОРДА
Автоустановка зависимостей + запуск
"""

import sys
import os
import subprocess
import urllib.request
import tempfile

def install_and_import():
    """Установка и импорт зависимостей"""
    try:
        # Пробуем импортировать Flask
        from flask import Flask, request, jsonify, render_template_string
        import sqlite3
        import datetime
        import hashlib
        return Flask, request, jsonify, render_template_string, sqlite3, datetime, hashlib
    except ImportError:
        print("📦 Установка Flask...")
        try:
            # Устанавливаем Flask
            subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ Flask установлен!")
            
            # Перезапускаем скрипт с установленными зависимостями
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except subprocess.CalledProcessError:
            print("❌ Ошибка установки Flask")
            print("Установите вручную: pip install flask")
            sys.exit(1)

# Устанавливаем и импортируем зависимости
Flask, request, jsonify, render_template_string, sqlite3, datetime, hashlib = install_and_import()

# ОСНОВНОЙ КОД СЕРВЕРА
app = Flask(__name__)
DB_FILE = "online_board.db"

MAIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Анонимная Онлайн Борда</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial; margin: 20px; background: #f0f0f0; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .logo { text-align: center; font-family: monospace; background: black; color: lime; padding: 10px; border-radius: 5px; }
        .topic { border: 1px solid #ccc; margin: 10px 0; padding: 15px; border-radius: 5px; background: #f9f9f9; }
        .topic-title { font-size: 1.2em; font-weight: bold; color: #333; }
        .topic-meta { color: #666; font-size: 0.9em; margin: 5px 0; }
        .topic-content { margin: 10px 0; white-space: pre-wrap; background: white; padding: 10px; border-radius: 3px; }
        form { margin: 20px 0; }
        input, textarea { width: 100%; margin: 5px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { background: #007cba; color: white; padding: 12px 25px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #005a87; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h2>DOX BIN</h2>
            <p>БУРГЕРЫ</p>
        </div>

        <h3>📝 Создать новую тему</h3>
        <form action="/create" method="post">
            <input type="text" name="title" placeholder="Заголовок темы" required>
            <textarea name="content" placeholder="Текст сообщения" rows="6" required></textarea>
            <button type="submit">📤 Опубликовать тему</button>
        </form>

        <h3>📂 Все темы ({{ topics_count }})</h3>
        {% if topics %}
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
        {% else %}
            <p>📭 Тем пока нет. Будьте первым!</p>
        {% endif %}

        <div style="text-align: center; margin-top: 20px; color: #666; font-size: 0.9em;">
            🔄 Страница обновляется каждые 30 секунд | 
            📱 Доступно с любого устройства
        </div>
    </div>

    <script>
        // Автообновление страницы
        setTimeout(() => { location.reload(); }, 30000);
        
        // Подтверждение отправки
        document.querySelector('form').addEventListener('submit', function(e) {
            if(!confirm('Отправить тему? После публикации редактирование будет невозможно!')) {
                e.preventDefault();
            }
        });
    </script>
</body>
</html>
'''

SUCCESS_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Тема создана!</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial; text-align: center; margin-top: 50px; }
        .success { background: #d4edda; padding: 20px; border-radius: 10px; margin: 20px auto; max-width: 500px; }
    </style>
</head>
<body>
    <div class="success">
        <h1>✅ Тема успешно создана!</h1>
        <p><strong>ID темы:</strong> {{ topic_id }}</p>
        <p>🔗 <strong>Ссылка для друзей:</strong></p>
        <code style="background: #f8f9fa; padding: 10px; display: block; margin: 10px;">{{ url }}</code>
        <a href="/" style="display: inline-block; margin-top: 15px; padding: 10px 20px; background: #007cba; color: white; text-decoration: none; border-radius: 5px;">← Вернуться к борде</a>
    </div>
</body>
</html>
'''

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
            'timestamp': row[3][:16],  # Обрезаем до даты и времени
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
    
    if not title.strip() or not content.strip():
        return "❌ Заголовок и текст не могут быть пустыми!", 400
    
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
    """API для получения тем"""
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

def start_server():
    """Запуск сервера"""
    init_database()
    print("🚀" * 50)
    print("🌐 АНОНИМНАЯ ОНЛАЙН БОРДА ЗАПУЩЕНА!")
    print("🚀" * 50)
    print("\n📊 Локальный доступ: http://localhost:5000")
    print("📱 Откройте эту ссылку в браузере")
    print("\n🌍 Чтобы сделать доступным из интернета:")
    print("   1. Откройте новый терминал")
    print("   2. Выполните: ngrok http 5000")
    print("   3. Или: ssh -R 80:localhost:5000 nokey@localhost.run")
    print("\n⏹️  Для остановки: Ctrl+C")
    print("─" * 50)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("⚠️  Попробуйте другой порт: python online_board.py --port 8080")

if __name__ == '__main__':
    start_server()