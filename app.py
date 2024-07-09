from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///registrations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define SQLAlchemy models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Seat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seat_number = db.Column(db.Integer, nullable=False)
    is_booked = db.Column(db.Boolean, default=False)

# Forms using WTForms
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class HelpForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Initialize seats
def initialize_seats(num_seats):
    with app.app_context():
        Seat.query.delete()
        for i in range(1, num_seats + 1):
            seat = Seat(seat_number=i)
            db.session.add(seat)
        db.session.commit()

# Routes
@app.route('/')
def index():
    seats = Seat.query.all()
    return render_template('index.html', seats=seats)

@app.route('/book_seat', methods=['POST'])
def book_seat():
    seat_number = int(request.form['seat_number'])
    seat = Seat.query.filter_by(seat_number=seat_number).first()
    
    if seat and not seat.is_booked:
        seat.is_booked = True
        db.session.commit()
        return "Your seat is booked successfully!"
    else:
        return "Seat already booked or invalid seat number."


@app.route('/booked_seats')
def booked_seats():
    booked_seats = Seat.query.filter_by(is_booked=True).all()
    return render_template( 'booked_seats.html', booked_seats=booked_seats)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            return redirect(url_for('index'))
        else:
            return render_template('login.html', form=form, message='Invalid username or password.')

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('register.html', form=form, message='Email already registered.')

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            return render_template('registration_confirmation.html', username=username)
        except Exception as e:
            db.session.rollback()
            return render_template('register.html', form=form, message='Error registering user.')

    return render_template('register.html', form=form)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        # Handle contact form submission
        return redirect(url_for('index'))
    return render_template('contact.html')

@app.route('/help', methods=['GET', 'POST'])
def help():
    form = HelpForm()
    if form.validate_on_submit():
        # Handle help form submission
        return redirect(url_for('index'))
    return render_template('help.html', form=form)

if __name__ == '__main__':
    with app.app_context():
        initialize_seats(10)  # Initialize 10 seats
    app.run(debug=True)
