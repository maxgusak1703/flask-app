# Проєкт "Школа знань"

Це простий блог-застосунок, створений на Flask. Є реєстрація, можна надсилати відгуки, а також деякі запитання, які зберігаються в БД.

![image](https://github.com/user-attachments/assets/54a9ed58-053a-42b9-9733-c67055ede6e4)

![image](https://github.com/user-attachments/assets/e8289eba-90b8-42cf-84e2-40bbe8131466)

![image](https://github.com/user-attachments/assets/16bfc943-77f9-41c5-b790-472b4cf8b443)


## Як запустити

1. Клонування репозиторію
```bash
git clone https://github.com/maxgusak1703/flask-app.git
cd flask-app
```
2. Створення віртуального середовища
```bash
python -m venv venv
```
- Windows:
```bash
venv\Scripts\activate
```
- Linux/macOS:
```bash
source venv/bin/activate
```
3. Встановлення залежностей
```bash
pip install -r requirements.txt
```
4. Запуск застосунку
```bash
flask run
```
В базі вже є один адміністратор: login - admin@gmail.com, pass - admin