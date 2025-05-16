from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
app.secret_key = '9jfs!2#lf8^sdl3k21@k2msd9f2'



class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)             
    email = db.Column(db.String(120), nullable=False)            
    subject = db.Column(db.String(150), nullable=False)           
    message = db.Column(db.Text, nullable=False)                 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"ContactMessage('{self.name}', '{self.email}', '{self.subject}')"

class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Testimonial('{self.name}', '{self.email}', '{self.category}', '{self.text}')"


with app.app_context():
    db.create_all()


@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/programs')
def programs():
    return render_template('programs.html')

@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        new_message = ContactMessage(name=name, email=email, subject=subject, message=message)
        try:
            db.session.add(new_message)
            db.session.commit()
        except:
            flash("Виникла помилка при надсиланні повідомлення", "danger")
        finally:
            db.session.close()
        
        flash("Ваше повідомлення надіслано успішно!", "success")
        return redirect(url_for('contacts'))
    return render_template('contacts.html')


@app.template_filter('datetimeformat')
def datetimeformat(value):
    if value is None:
        return ""
    months = {
        1: 'січня', 2: 'лютого', 3: 'березня', 4: 'квітня',
        5: 'травня', 6: 'червня', 7: 'липня', 8: 'серпня',
        9: 'вересня', 10: 'жовтня', 11: 'листопада', 12: 'грудня'
    }
    return f"{value.day} {months[value.month]} {value.year}, {value.strftime('%H:%M')}"


@app.route('/testimonials', methods=['GET', 'POST'])
def testimonials():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        category = request.form.get('category')
        testimonial = request.form.get('testimonial')

        if not all([name, email, category, testimonial]):
            flash('Будь ласка, заповніть усі обов’язкові поля.', 'danger')
        else:
            try:
                new_testimonial = Testimonial(
                    name=name,
                    email=email,
                    category=category,
                    text=testimonial
                )
                db.session.add(new_testimonial)
                db.session.commit()
                flash('Відгук успішно створено!', 'success')
            except Exception as e:
                flash(f'Помилка: {str(e)}', 'danger')
            finally:
                db.session.close()
        return redirect(url_for('testimonials'))

    testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).all()
    return render_template('testimonials.html', testimonials=testimonials)

    
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500



if __name__ == '__main__':
    app.run(debug=True)  