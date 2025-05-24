from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '9jfs!2#lf8^sdl3k21@k2msd9f2'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' 
login_manager.login_message = 'Вам потрібно увійти, щоб отримати доступ до цієї сторінки.'
login_manager.login_message_category = 'info'  

import routes, models

with app.app_context():
    db.create_all()
    
    

if __name__ == "__main__":
    app.run(debug=True)

