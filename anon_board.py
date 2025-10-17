import sqlite3
import datetime
import hashlib
import os
import sys
from typing import List, Dict, Optional

class AnonBoard:
    def __init__(self, db_name: str = "anon_board.db"):
        self.db_name = db_name
        self.logo_art = """

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
        """
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topics (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                author_ip TEXT DEFAULT 'local'
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id TEXT PRIMARY KEY,
                topic_id TEXT,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                author_ip TEXT DEFAULT 'local',
                FOREIGN KEY (topic_id) REFERENCES topics (id)
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ База данных инициализирована")
    
    def generate_id(self, text: str) -> str:
        """Генерация уникального ID"""
        return hashlib.md5(
            f"{text}{datetime.datetime.now().isoformat()}".encode()
        ).hexdigest()[:10]
    
    def create_topic(self, title: str, content: str) -> str:
        """Создание новой темы"""
        topic_id = self.generate_id(title + content)
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO topics (id, title, content, timestamp, author_ip)
            VALUES (?, ?, ?, ?, ?)
        ''', (topic_id, title, content, 
              datetime.datetime.now().isoformat(), 'local'))
        conn.commit()
        conn.close()
        
        return topic_id
    
    def add_comment(self, topic_id: str, content: str) -> bool:
        """Добавление комментария к теме"""
        # Проверяем существование темы
        if not self.get_topic(topic_id):
            return False
        
        comment_id = self.generate_id(content)
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO comments (id, topic_id, content, timestamp, author_ip)
            VALUES (?, ?, ?, ?, ?)
        ''', (comment_id, topic_id, content,
              datetime.datetime.now().isoformat(), 'local'))
        conn.commit()
        conn.close()
        
        return True
    
    def get_all_topics(self) -> List[Dict]:
        """Получение всех тем"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, content, timestamp, author_ip 
            FROM topics 
            ORDER BY timestamp DESC
        ''')
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
        return topics
    
    def get_topic(self, topic_id: str) -> Optional[Dict]:
        """Получение темы по ID"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, content, timestamp, author_ip 
            FROM topics 
            WHERE id = ?
        ''', (topic_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        topic = {
            'id': row[0],
            'title': row[1],
            'content': row[2],
            'timestamp': row[3],
            'author_ip': row[4]
        }
        
        # Получаем комментарии
        cursor.execute('''
            SELECT content, timestamp, author_ip 
            FROM comments 
            WHERE topic_id = ? 
            ORDER BY timestamp ASC
        ''', (topic_id,))
        
        topic['comments'] = [
            {'content': row[0], 'timestamp': row[1], 'author_ip': row[2]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return topic
    
    def search_topics(self, query: str) -> List[Dict]:
        """Поиск тем по заголовку и содержанию"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, content, timestamp, author_ip 
            FROM topics 
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY timestamp DESC
        ''', (f'%{query}%', f'%{query}%'))
        
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
        return topics
    
    def get_stats(self) -> Dict:
        """Статистика борды"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM topics')
        topic_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM comments')
        comment_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT timestamp FROM topics ORDER BY timestamp DESC LIMIT 1')
        last_post = cursor.fetchone()
        
        conn.close()
        
        return {
            'topics': topic_count,
            'comments': comment_count,
            'last_post': last_post[0] if last_post else 'Нет постов'
        }


class TerminalUI:
    def __init__(self):
        self.board = AnonBoard()
        self.clear_screen()
    
    def clear_screen(self):
        """Очистка экрана"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_logo(self):
        """Вывод логотипа"""
        print("\033[1;36m")  # Голубой цвет
        print(self.board.logo_art)
        print("\033[0m")  # Сброс цвета
    
    def print_header(self, title: str):
        """Заголовок раздела"""
        print(f"\n\033[1;33m{'='*60}\033[0m")
        print(f"\033[1;33m{title:^60}\033[0m")
        print(f"\033[1;33m{'='*60}\033[0m")
    
    def wait_for_enter(self):
        """Ожидание нажатия Enter"""
        input("\n\033[1;30mНажмите Enter для продолжения...\033[0m")
    
    def create_topic_ui(self):
        """Интерфейс создания темы"""
        self.clear_screen()
        self.print_logo()
        self.print_header("СОЗДАНИЕ НОВОЙ ТЕМЫ")
        
        title = input("\n📝 Заголовок темы: ").strip()
        if not title:
            print("❌ Заголовок не может быть пустым!")
            self.wait_for_enter()
            return
        
        print("\n📄 Текст темы (введите END на отдельной строке для завершения):")
        print("\033[1;30m" + "─" * 50 + "\033[0m")
        
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        
        content = "\n".join(lines)
        if not content.strip():
            print("❌ Текст темы не может быть пустым!")
            self.wait_for_enter()
            return
        
        topic_id = self.board.create_topic(title, content)
        
        print(f"\n✅ Тема успешно создана!")
        print(f"🔑 ID темы: {topic_id}")
        self.wait_for_enter()
    
    def view_topics_ui(self):
        """Просмотр всех тем"""
        self.clear_screen()
        self.print_logo()
        self.print_header("ВСЕ ТЕМЫ")
        
        topics = self.board.get_all_topics()
        
        if not topics:
            print("📭 Тем пока нет...")
            self.wait_for_enter()
            return
        
        for i, topic in enumerate(topics, 1):
            print(f"\n\033[1;32m{i}. {topic['title']}\033[0m")
            print(f"   🔑 ID: {topic['id']}")
            print(f"   🕐 {topic['timestamp'][:16]}")
            preview = topic['content'][:100] + "..." if len(topic['content']) > 100 else topic['content']
            print(f"   📄 {preview}")
            print("   " + "─" * 50)
        
        print(f"\n📊 Всего тем: {len(topics)}")
        self.wait_for_enter()
    
    def view_topic_ui(self):
        """Просмотр конкретной темы"""
        self.clear_screen()
        self.print_logo()
        self.print_header("ПРОСМОТР ТЕМЫ")
        
        topic_id = input("Введите ID темы: ").strip()
        if not topic_id:
            print("❌ ID не может быть пустым!")
            self.wait_for_enter()
            return
        
        topic = self.board.get_topic(topic_id)
        if not topic:
            print("❌ Тема не найдена!")
            self.wait_for_enter()
            return
        
        self.clear_screen()
        self.print_logo()
        print(f"\n\033[1;32m{topic['title']}\033[0m")
        print(f"🔑 ID: {topic['id']}")
        print(f"🕐 {topic['timestamp']}")
        print(f"👤 Автор: {topic['author_ip']}")
        print("\033[1;34m" + "=" * 60 + "\033[0m")
        print(topic['content'])
        print("\033[1;34m" + "=" * 60 + "\033[0m")
        
        # Комментарии
        if topic.get('comments'):
            print(f"\n💬 Комментарии ({len(topic['comments'])}):")
            for comment in topic['comments']:
                print(f"\n┌─ {comment['timestamp'][:16]}")
                print(f"└─ {comment['content']}")
        else:
            print("\n💬 Комментариев пока нет")
        
        # Добавление комментария
        add_comment = input("\n📝 Добавить комментарий? (y/n): ").lower()
        if add_comment == 'y':
            comment_text = input("Текст комментария: ").strip()
            if comment_text:
                if self.board.add_comment(topic_id, comment_text):
                    print("✅ Комментарий добавлен!")
                else:
                    print("❌ Ошибка добавления комментария")
        
        self.wait_for_enter()
    
    def search_ui(self):
        """Поиск тем"""
        self.clear_screen()
        self.print_logo()
        self.print_header("ПОИСК ТЕМ")
        
        query = input("Введите поисковый запрос: ").strip()
        if not query:
            print("❌ Запрос не может быть пустым!")
            self.wait_for_enter()
            return
        
        results = self.board.search_topics(query)
        
        print(f"\n🔍 Найдено тем: {len(results)}")
        
        for i, topic in enumerate(results, 1):
            print(f"\n\033[1;32m{i}. {topic['title']}\033[0m")
            print(f"   🔑 ID: {topic['id']}")
            print(f"   🕐 {topic['timestamp'][:16]}")
        
        self.wait_for_enter()
    
    def stats_ui(self):
        """Статистика"""
        self.clear_screen()
        self.print_logo()
        self.print_header("СТАТИСТИКА")
        
        stats = self.board.get_stats()
        
        print(f"📊 Тем: {stats['topics']}")
        print(f"💬 Комментариев: {stats['comments']}")
        print(f"🕐 Последний пост: {stats['last_post']}")
        
        self.wait_for_enter()
    
    def main_menu(self):
        """Главное меню"""
        while True:
            self.clear_screen()
            self.print_logo()
            
            print("\n\033[1;35mГЛАВНОЕ МЕНЮ:\033[0m")
            print("1. 📝 Создать тему")
            print("2. 📂 Просмотреть все темы") 
            print("3. 🔍 Поиск тем")
            print("4. 📊 Статистика")
            print("5. 🚪 Выход")
            
            choice = input("\nВыберите действие (1-5): ").strip()
            
            if choice == '1':
                self.create_topic_ui()
            elif choice == '2':
                self.view_topics_ui()
            elif choice == '3':
                self.search_ui()
            elif choice == '4':
                self.stats_ui()
            elif choice == '5':
                print("\n👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор!")
                self.wait_for_enter()


if __name__ == "__main__":
    try:
        ui = TerminalUI()
        ui.main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Программа завершена!")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")