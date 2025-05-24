from flask import render_template, request, redirect, flash, url_for
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db
from models import User, ContactMessage, Testimonial
import bcrypt

# Фільтр для форматування дати
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

from app import login_manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Головні сторінки
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

# Реєстрація
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        category = request.form.get('category')
        confirm_password = request.form.get('confirm_password')

        if not all([username, email, password, category, confirm_password]):
            flash('Заповніть усі поля.', 'danger')
        elif password != confirm_password:
            flash('Паролі не співпадають.', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('Це ім’я користувача вже зайнято.', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('Ця електронна пошта вже використовується.', 'danger')
        else:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            try:
                user = User(username=username, email=email, category=category, password=hashed_password)
                db.session.add(user)
                db.session.commit()
            except:
                flash('Помилка при створенні облікового запису.', 'danger')
            flash('Ваш обліковий запис створено!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

# Логін
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Невірна електронна пошта або пароль.', 'danger')
    return render_template('login.html', title='Вхід')

# Профіль
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        category = request.form.get('category')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([username, email, category]):
            flash('Заповніть ім’я користувача, email та категорію.', 'danger')
        elif username != current_user.username and User.query.filter_by(username=username).first():
            flash('Це ім’я користувача вже зайнято.', 'danger')
        elif email != current_user.email and User.query.filter_by(email=email).first():
            flash('Ця електронна пошта вже використовується.', 'danger')
        elif category not in ['admin', 'parents', 'students', 'graduates']:
            flash('Невірна категорія.', 'danger')
        else:
            current_user.username = username
            current_user.email = email
            current_user.category = category

            if password or confirm_password:
                if password != confirm_password:
                    flash('Паролі не співпадають.', 'danger')
                else:
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    current_user.password = hashed_password

            db.session.commit()
            flash('Профіль оновлено!', 'success')
            return redirect(url_for('profile'))

    return render_template('profile.html', title='Профіль', user=current_user)

# Вихід
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Контакти
@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        if not all([name, email, subject, message]):
            flash('Заповніть усі поля.', 'danger')
        else:
            try:
                new_message = ContactMessage(name=name, email=email, subject=subject, message=message)
                db.session.add(new_message)
                db.session.commit()
                flash('Ваше повідомлення надіслано успішно!', 'success')
            except Exception as e:
                flash(f'Помилка: {str(e)}', 'danger')
        return redirect(url_for('contacts'))
    return render_template('contacts.html', title='Контакти')

# Відгуки
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
                    text=testimonial,
                    is_approved=False 
                )
                db.session.add(new_testimonial)
                db.session.commit()
                flash('Відгук надіслано на модерацію.', 'success')
            except Exception as e:
                flash(f'Помилка: {str(e)}', 'danger')
        return redirect(url_for('testimonials'))
    testimonials = Testimonial.query.filter_by(is_approved=True).order_by(Testimonial.created_at.desc()).all()
    return render_template('testimonials.html', title='Відгуки', testimonials=testimonials)


# Адмін-панель
@app.route('/admin', methods=['GET'])
@login_required
def admin():
    if not current_user.is_admin:
        flash('Доступ дозволено лише адміністраторам.', 'danger')
        return redirect(url_for('index'))
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).all()
    users = User.query.order_by(User.username).all()
    return render_template('admin.html', title='Адмін-панель', users=users, messages=messages, testimonials=testimonials)

# Видалення повідомлення
@app.route('/admin/delete_message/<int:message_id>')
@login_required
def delete_message(message_id):
    if not current_user.is_admin:
        flash('Доступ дозволено лише адміністраторам.', 'danger')
        return redirect(url_for('index'))
    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    flash('Повідомлення видалено!', 'success')
    return redirect(url_for('admin'))

# Схвалення відгуку
@app.route('/admin/approve_testimonial/<int:testimonial_id>')
@login_required
def approve_testimonial(testimonial_id):
    if not current_user.is_admin:
        flash('Доступ дозволено лише адміністраторам.', 'danger')
        return redirect(url_for('index'))
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    testimonial.is_approved = True
    db.session.commit()
    flash('Відгук схвалено!', 'success')
    return redirect(url_for('admin'))

# Видалення відгуку
@app.route('/admin/delete_testimonial/<int:testimonial_id>')
@login_required
def delete_testimonial(testimonial_id):
    if not current_user.is_admin:
        flash('Доступ дозволено лише адміністраторам.', 'danger')
        return redirect(url_for('index'))
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    db.session.delete(testimonial)
    db.session.commit()
    flash('Відгук видалено!', 'success')
    return redirect(url_for('admin'))

# Видалення користувача
@app.route('/admin/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Доступ дозволено лише адміністраторам.', 'danger')
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Користувача видалено!', 'success')
    return redirect(url_for('admin'))


# Редагування користувача
@app.route('/admin/toggle_admin/<int:user_id>')
@login_required
def toggle_admin(user_id):
    if not current_user.is_admin:
        flash('Доступ дозволено лише адміністраторам.', 'danger')
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Ви не можете змінити власний статус адміністратора.', 'danger')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        status = 'призначено адміністратором' if user.is_admin else 'знято права адміністратора'
        flash(f'Користувач {user.username} {status}.', 'success')
    return redirect(url_for('admin'))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500