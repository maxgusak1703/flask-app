import os
from flask import render_template, request, redirect, flash, url_for
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db
from models import User, ContactMessage, Testimonial
from forms import RegistrationForm, LoginForm, ContactForm, TestimonialForm, ProfileForm
from werkzeug.utils import secure_filename
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

def save_profile_image(form_file, username):
    if not form_file:
        return None
    filename = secure_filename(f"{username}_{form_file.filename}")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    form_file.save(filepath)
    return f"uploads/{filename}"

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
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        try:
            user = User(username=form.username.data, email=form.email.data, category=form.category.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
        except:
            flash('Помилка при створенні облікового запису.', 'danger')
        flash('Ваш обліковий запис створено!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Логін
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Невірна електронна пошта або пароль.', 'danger')

    return render_template('login.html', form=form)

# Профіль
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if not current_user.is_authenticated:
        flash('Вам потрібно увійти, щоб отримати доступ до профілю.', 'warning')
        return redirect(url_for('login'))
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.category = form.category.data
        if not current_user.is_admin:
            flash('Ви не маєте прав для зміни категорії на "Адміністратор".', 'danger')
            return redirect(url_for('profile'))
        if form.password.data:
            hashed_password = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            current_user.password = hashed_password
        if form.profile_image.data:
            profile_image = save_profile_image(form.profile_image.data, current_user.username)
            if profile_image:
                current_user.profile_image = profile_image
        db.session.commit()
        flash('Профіль оновлено!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.category.data = current_user.category
    return render_template('profile.html', title='Мій профіль - Школа "Знання"', form=form, user=current_user)

# Вихід
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Контакти
@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        subject = form.subject.data
        message = form.message.data
        try:
            new_message = ContactMessage(name=name, email=email, subject=subject, message=message)
            db.session.add(new_message)
            db.session.commit()
            flash('Ваше повідомлення надіслано успішно!', 'success')
        except Exception as e:
            flash(f'Помилка: {str(e)}', 'danger')
        return redirect(url_for('contacts'))
    return render_template('contacts.html', title='Контакти', form=form)

# Відгуки
@app.route('/testimonials', methods=['GET', 'POST'])
def testimonials():
    form = TestimonialForm()
    if form.validate_on_submit():
        try:
            new_testimonial = Testimonial(
                name=form.name.data,
                email=form.email.data,
                category=form.category.data,
                text=form.text.data,
                is_approved=False
            )
            db.session.add(new_testimonial)
            db.session.commit()
            flash('Відгук надіслано на модерацію.', 'success')
        except Exception as e:
            flash(f'Помилка: {str(e)}', 'danger')
        return redirect(url_for('testimonials'))
    testimonials = Testimonial.query.filter_by(is_approved=True).order_by(Testimonial.created_at.desc()).all()
    return render_template('testimonials.html', title='Відгуки', testimonials=testimonials, form=form)

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