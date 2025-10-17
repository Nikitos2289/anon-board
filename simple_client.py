import requests
import os

def main():
    server = input("🌐 Адрес сервера (например: http://localhost:5000): ").strip()
    if not server:
        server = "http://localhost:5000"
    
    while True:
        os.system('cls')
        print("🌐 Анонимная Борда")
        print("1. 📂 Темы")
        print("2. 📝 Создать")
        print("3. 🚪 Выход")
        
        choice = input("Выберите: ")
        
        if choice == '1':
            topics = requests.get(f"{server}/api/topics").json()
            for topic in topics:
                print(f"\n{topic['title']}")
                print(f"ID: {topic['id']}")
                print(topic['content'][:100] + "...")
            input("\n↵ Enter...")
        elif choice == '2':
            title = input("Заголовок: ")
            content = input("Текст: ")
            requests.post(f"{server}/api/create", json={"title": title, "content": content})
            print("✅ Создано!")
            input("↵ Enter...")
        elif choice == '3':
            break

if __name__ == "__main__":
    main()