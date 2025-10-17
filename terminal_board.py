#!/usr/bin/env python3
"""
АНОНИМНАЯ ТЕРМИНАЛЬНАЯ БОРДА
Скачать и запустить отдельно
"""

import sys
import os
import subprocess
import json
import datetime
import hashlib
import threading
import time

def install_dependencies():
    """Установка всех необходимых зависимостей"""
    try:
        import flask
        import requests
        import sqlite3
        return True
    except ImportError as e:
        print(f"📦 Установка зависимостей...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "flask", "requests"
            ])
            print("✅ Зависимости установлены!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Ошибка установки. Установите вручную: pip install flask requests")
            return False

# Устанавливаем зависимости
if not install_dependencies():
    sys.exit(1)

# Импортируем после установки
import flask
import requests
import sqlite3
from flask import Flask, request, jsonify

# ================== ВЕБ-СЕРВЕР ==================
app = Flask(__name__)
DB_FILE = "shared_board.db"

def init_database():
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

@app.route('/api/topics', methods=['GET'])
def get_topics():
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
def create_topic():
    data = request.get_json()
    
    topic_id = hashlib.md5(f"{data['title']}{data['content']}{datetime.datetime.now()}".encode()).hexdigest()[:10]
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO topics (id, title, content, timestamp, author_ip)
        VALUES (?, ?, ?, ?, ?)
    ''', (topic_id, data['title'], data['content'], 
          datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), request.remote_addr))
    
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "topic_id": topic_id})

def start_server():
    init_database()
    print("🌐 Сервер запущен: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# ================== КЛИЕНТ ==================
class TerminalBoard:
    def __init__(self, server_url="http://localhost:5000"):
        self.server_url = server_url
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_menu(self):
        self.clear_screen()
        print("""
╔═══════════════════════════════════════════════╗
║            🌐 АНОНИМНАЯ БОРДА 🌐             ║
║              🖥️  ТЕРМИНАЛЬНАЯ ВЕРСИЯ           ║
║         🚫 РЕДАКТИРОВАНИЕ ЗАПРЕЩЕНО          ║
╚═══════════════════════════════════════════════╝

📍 ГЛАВНОЕ МЕНЮ:
1. 📝 Создать тему
2. 📂 Все темы
3. 📖 Найти тему по ID
4. 🔍 Поиск по тексту
5. 📊 Статистика
6. 🚪 Выход
        """)
    
    def get_topics(self):
        try:
            response = requests.get(f"{self.server_url}/api/topics")
            return response.json() if response.status_code == 200 else []
        except:
            return []
    
    def create_topic(self):
        self.clear_screen()
        print("📝 СОЗДАНИЕ ТЕМЫ")
        print("─" * 30)
        
        title = input("Заголовок: ").strip()
        if not title:
            return
        
        print("Текст (пустая строка для завершения):")
        lines = []
        while True:
            line = input()
            if not line.strip():
                break
            lines.append(line)
        
        content = "\n".join(lines)
        if not content.strip():
            return
        
        result = requests.post(f"{self.server_url}/api/create", 
                             json={"title": title, "content": content})
        
        if result.json().get("status") == "success":
            print("✅ Тема создана!")
        else:
            print("❌ Ошибка!")
        
        input("↵ Нажмите Enter...")
    
    def view_topics(self):
        self.clear_screen()
        print("📂 ВСЕ ТЕМЫ")
        print("─" * 30)
        
        topics = self.get_topics()
        
        for i, topic in enumerate(topics, 1):
            print(f"\n{i}. {topic['title']}")
            print(f"   ID: {topic['id']}")
            print(f"   {topic['timestamp']}")
            preview = topic['content'][:80] + "..." if len(topic['content']) > 80 else topic['content']
            print(f"   {preview}")
        
        print(f"\nВсего: {len(topics)} тем")
        input("\n↵ Нажмите Enter...")
    
    def search_id(self):
        self.clear_screen()
        print("📖 ПОИСК ПО ID")
        print("─" * 30)
        
        topic_id = input("ID темы: ").strip()
        if not topic_id:
            return
        
        topics = self.get_topics()
        for topic in topics:
            if topic['id'] == topic_id:
                print(f"\n📖 {topic['title']}")
                print(f"🕐 {topic['timestamp']}")
                print(f"👤 {topic['author_ip']}")
                print(f"\n{topic['content']}")
                break
        else:
            print("❌ Тема не найдена!")
        
        input("\n↵ Нажмите Enter...")
    
    def search_text(self):
        self.clear_screen()
        print("🔍 ПОИСК ПО ТЕКСТУ")
        print("─" * 30)
        
        query = input("Поиск: ").strip()
        if not query:
            return
        
        topics = self.get_topics()
        found = [t for t in topics if query.lower() in t['title'].lower() or query.lower() in t['content'].lower()]
        
        print(f"\nНайдено: {len(found)} тем")
        for i, topic in enumerate(found, 1):
            print(f"\n{i}. {topic['title']}")
            print(f"   ID: {topic['id']}")
        
        input("\n↵ Нажмите Enter...")
    
    def show_stats(self):
        self.clear_screen()
        print("📊 СТАТИСТИКА")
        print("─" * 30)
        
        topics = self.get_topics()
        print(f"Тем: {len(topics)}")
        print(f"Сервер: {self.server_url}")
        
        input("\n↵ Нажмите Enter...")
    
    def run(self):
        while True:
            self.print_menu()
            choice = input("🎯 Выберите (1-6): ").strip()
            
            if choice == '1':
                self.create_topic()
            elif choice == '2':
                self.view_topics()
            elif choice == '3':
                self.search_id()
            elif choice == '4':
                self.search_text()
            elif choice == '5':
                self.show_stats()
            elif choice == '6':
                print("👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор!")
                input("↵ Нажмите Enter...")

# ================== ЗАПУСК ==================
def main():
    print("🚀 Запуск Анонимной Борды...")
    
    # Запуск сервера в фоне
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(2)
    
    # Запуск клиента
    client = TerminalBoard()
    client.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Завершено!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")