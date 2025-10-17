#!/usr/bin/env python3
"""
АНОНИМНАЯ ТЕРМИНАЛЬНАЯ БОРДА
Онлайн в терминале + Веб-сервер для синхронизации
"""

import sys
import os
import requests
import json
import datetime
import hashlib
from flask import Flask, request, jsonify

# ================== ВЕБ-СЕРВЕР ДЛЯ СИНХРОНИЗАЦИИ ==================
app = Flask(__name__)
DB_FILE = "shared_board.db"

def init_database():
    """Инициализация базы данных"""
    import sqlite3
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
    """Получить все темы"""
    import sqlite3
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
    """Создать тему"""
    import sqlite3
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
    """Запуск сервера синхронизации"""
    init_database()
    print("🌐 Сервер синхронизации запущен на http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# ================== ТЕРМИНАЛЬНЫЙ КЛИЕНТ ==================
class TerminalBoard:
    def __init__(self, server_url="http://localhost:5000"):
        self.server_url = server_url
        self.logo = """
╔═══════════════════════════════════════════════╗
║            🌐 АНОНИМНАЯ БОРДА 🌐             ║
║              🖥️  ТЕРМИНАЛЬНАЯ ВЕРСИЯ           ║
║         🚫 РЕДАКТИРОВАНИЕ ЗАПРЕЩЕНО          ║
╚═══════════════════════════════════════════════╝
        """
    
    def clear_screen(self):
        """Очистка экрана"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title):
        """Печать заголовка"""
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    
    def wait_enter(self):
        """Ожидание Enter"""
        input("\n↵ Нажмите Enter для продолжения...")
    
    def get_topics(self):
        """Получить темы с сервера"""
        try:
            response = requests.get(f"{self.server_url}/api/topics")
            if response.status_code == 200:
                return response.json()
            else:
                print("❌ Ошибка получения тем")
                return []
        except:
            print("❌ Сервер недоступен")
            return []
    
    def create_topic(self, title, content):
        """Создать тему на сервере"""
        try:
            response = requests.post(f"{self.server_url}/api/create", 
                                   json={"title": title, "content": content})
            return response.json()
        except:
            return {"status": "error", "message": "Сервер недоступен"}
    
    def view_all_topics(self):
        """Просмотр всех тем"""
        self.clear_screen()
        print(self.logo)
        self.print_header("📂 ВСЕ ТЕМЫ")
        
        topics = self.get_topics()
        
        if not topics:
            print("📭 Тем пока нет...")
            self.wait_enter()
            return
        
        for i, topic in enumerate(topics, 1):
            print(f"\n📌 ТЕМА #{i}")
            print(f"   🏷️  {topic['title']}")
            print(f"   🔑 ID: {topic['id']}")
            print(f"   🕐 {topic['timestamp']}")
            print(f"   👤 {topic['author_ip']}")
            print(f"   📄 {topic['content'][:100]}{'...' if len(topic['content']) > 100 else ''}")
            print("   " + "─" * 50)
        
        print(f"\n📊 Всего тем: {len(topics)}")
        self.wait_enter()
    
    def create_new_topic(self):
        """Создание новой темы"""
        self.clear_screen()
        print(self.logo)
        self.print_header("📝 СОЗДАНИЕ ТЕМЫ")
        
        print("\nВведите данные темы:")
        print("─" * 40)
        
        title = input("🏷️  Заголовок: ").strip()
        if not title:
            print("❌ Заголовок не может быть пустым!")
            self.wait_enter()
            return
        
        print("\n📄 Текст темы (введите END на новой строке для завершения):")
        print("─" * 40)
        
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            except EOFError:
                break
        
        content = "\n".join(lines)
        if not content.strip():
            print("❌ Текст темы не может быть пустым!")
            self.wait_enter()
            return
        
        print("\n⏳ Отправка на сервер...")
        result = self.create_topic(title, content)
        
        if result.get("status") == "success":
            print(f"✅ Тема создана! ID: {result['topic_id']}")
        else:
            print(f"❌ Ошибка: {result.get('message', 'Неизвестная ошибка')}")
        
        self.wait_enter()
    
    def search_topics(self):
        """Поиск тем"""
        self.clear_screen()
        print(self.logo)
        self.print_header("🔍 ПОИСК ТЕМ")
        
        query = input("Введите поисковый запрос: ").strip()
        if not query:
            print("❌ Запрос не может быть пустым!")
            self.wait_enter()
            return
        
        topics = self.get_topics()
        found = []
        
        for topic in topics:
            if query.lower() in topic['title'].lower() or query.lower() in topic['content'].lower():
                found.append(topic)
        
        print(f"\n🔍 Найдено тем: {len(found)}")
        
        for i, topic in enumerate(found, 1):
            print(f"\n📌 #{i} | {topic['title']}")
            print(f"   🔑 {topic['id']}")
            print(f"   📄 {topic['content'][:80]}...")
        
        self.wait_enter()
    
    def view_topic_detail(self):
        """Детальный просмотр темы"""
        self.clear_screen()
        print(self.logo)
        self.print_header("📖 ПРОСМОТР ТЕМЫ")
        
        topic_id = input("Введите ID темы: ").strip()
        if not topic_id:
            print("❌ ID не может быть пустым!")
            self.wait_enter()
            return
        
        topics = self.get_topics()
        topic = None
        
        for t in topics:
            if t['id'] == topic_id:
                topic = t
                break
        
        if not topic:
            print("❌ Тема не найдена!")
            self.wait_enter()
            return
        
        self.clear_screen()
        print(self.logo)
        self.print_header(f"📖 {topic['title']}")
        
        print(f"🔑 ID: {topic['id']}")
        print(f"🕐 Время: {topic['timestamp']}")
        print(f"👤 Автор: {topic['author_ip']}")
        print("\n" + "═" * 60)
        print(topic['content'])
        print("═" * 60)
        
        self.wait_enter()
    
    def show_stats(self):
        """Статистика"""
        self.clear_screen()
        print(self.logo)
        self.print_header("📊 СТАТИСТИКА")
        
        topics = self.get_topics()
        
        print(f"📂 Тем: {len(topics)}")
        
        if topics:
            latest = topics[0]
            print(f"🕐 Последняя тема: {latest['timestamp']}")
            print(f"📝 Заголовок: {latest['title']}")
        
        print(f"🌐 Сервер: {self.server_url}")
        self.wait_enter()
    
    def main_menu(self):
        """Главное меню"""
        while True:
            self.clear_screen()
            print(self.logo)
            
            print("\n📍 ГЛАВНОЕ МЕНЮ:")
            print("1. 📝 Создать тему")
            print("2. 📂 Все темы")
            print("3. 📖 Найти тему по ID") 
            print("4. 🔍 Поиск по тексту")
            print("5. 📊 Статистика")
            print("6. 🚪 Выход")
            
            choice = input("\n🎯 Выберите действие (1-6): ").strip()
            
            if choice == '1':
                self.create_new_topic()
            elif choice == '2':
                self.view_all_topics()
            elif choice == '3':
                self.view_topic_detail()
            elif choice == '4':
                self.search_topics()
            elif choice == '5':
                self.show_stats()
            elif choice == '6':
                print("\n👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор!")
                self.wait_enter()

# ================== ЗАПУСК ==================
def install_dependencies():
    """Установка зависимостей"""
    try:
        import flask
        import requests
    except ImportError:
        print("📦 Установка зависимостей...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "requests"])
        print("✅ Зависимости установлены!")
        # Перезапуск с установленными зависимостями
        os.execv(sys.executable, [sys.executable] + sys.argv)

def main():
    """Основная функция"""
    install_dependencies()
    
    print("🚀 Запуск Терминальной Борды...")
    print("🌐 Сервер синхронизации: http://localhost:5000")
    print("📱 Клиенты подключаются к этому адресу")
    print("\n💡 Для доступа из интернета выполните в отдельном терминале:")
    print("   ngrok http 5000")
    print("   ИЛИ")
    print("   ssh -R 80:localhost:5000 nokey@localhost.run")
    print("\n" + "═" * 50)
    
    # Запуск сервера в фоновом режиме
    import threading
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Даем серверу время запуститься
    import time
    time.sleep(2)
    
    # Запуск клиента
    client = TerminalBoard()
    client.main_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Программа завершена!")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")