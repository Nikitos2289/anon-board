#!/usr/bin/env python3
"""
ПРОСТОЙ КЛИЕНТ ДЛЯ ДРУЗЕЙ
Только терминал, без запуска сервера
"""

import requests
import sys
import os

def install_requests():
    """Установка requests если нет"""
    try:
        import requests
    except ImportError:
        print("📦 Установка requests...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        print("✅ requests установлен!")
        import requests
    return requests

class SimpleClient:
    def __init__(self, server_url):
        self.server_url = server_url
        self.requests = install_requests()
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_topics(self):
        """Показать все темы"""
        try:
            response = self.requests.get(f"{self.server_url}/api/topics")
            topics = response.json()
            
            print(f"\n📂 ВСЕ ТЕМЫ ({len(topics)}):")
            print("═" * 50)
            
            for i, topic in enumerate(topics, 1):
                print(f"\n📌 #{i} | {topic['title']}")
                print(f"   🔑 ID: {topic['id']}")
                print(f"   🕐 {topic['timestamp']}")
                print(f"   👤 {topic['author_ip']}")
                print(f"   📄 {topic['content'][:80]}...")
                print("   ─" * 25)
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def create_topic(self):
        """Создать тему"""
        print("\n📝 СОЗДАНИЕ ТЕМЫ:")
        print("─" * 30)
        
        title = input("Заголовок: ").strip()
        if not title:
            print("❌ Заголовок не может быть пустым!")
            return
        
        print("Текст (введите END на новой строке для завершения):")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        
        content = "\n".join(lines)
        if not content.strip():
            print("❌ Текст не может быть пустым!")
            return
        
        try:
            response = self.requests.post(f"{self.server_url}/api/create", 
                                        json={"title": title, "content": content})
            result = response.json()
            
            if result.get("status") == "success":
                print(f"✅ Тема создана! ID: {result['topic_id']}")
            else:
                print("❌ Ошибка создания темы")
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def main_menu(self):
        """Главное меню"""
        while True:
            self.clear_screen()
            print("""
╔═══════════════════════════════╗
║     🌐 АНОНИМНАЯ БОРДА       ║  
║        🖥️  КЛИЕНТ            ║
╚═══════════════════════════════╝
            """)
            
            print(f"🌐 Сервер: {self.server_url}")
            print("\n1. 📂 Показать все темы")
            print("2. 📝 Создать тему")
            print("3. 🚪 Выход")
            
            choice = input("\nВыберите действие: ").strip()
            
            if choice == '1':
                self.show_topics()
                input("\n↵ Нажмите Enter...")
            elif choice == '2':
                self.create_topic()
                input("\n↵ Нажмите Enter...")
            elif choice == '3':
                print("👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор!")
                input("\n↵ Нажмите Enter...")

def main():
    print("🌐 КЛИЕНТ АНОНИМНОЙ БОРДЫ")
    print("═" * 30)
    
    # Автоматическое определение сервера или запрос
    server_url = input("Введите адрес сервера (например: http://localhost:5000): ").strip()
    if not server_url:
        server_url = "http://localhost:5000"
    
    client = SimpleClient(server_url)
    client.main_menu()

if __name__ == "__main__":
    main()