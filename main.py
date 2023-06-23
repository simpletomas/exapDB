import datetime
import secrets
import pyotp as pyotp
from flask import Flask, request, jsonify, abort, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pandas as pd
import jwt
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accommodation.db'  # Підключення до бази даних
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Ініціалізація міграцій

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'dhomevibe01@gmail.com'
app.config['MAIL_PASSWORD'] = '115903Pink'

mail = Mail(app)


class Country(db.Model):
    __tablename__ = 'Country'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    # Додаткові поля для моделі Country


class City(db.Model):
    __tablename__ = 'City'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=False)


class Owner(db.Model):
    __tablename__ = 'Owner'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Owner {self.first_name} {self.last_name}>'


# Модель RentalProperty
class RentalProperty(db.Model):
    __tablename__ = 'Rental_Property'

    ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(255), nullable=False)
    Description = db.Column(db.String(255))
    Address = db.Column(db.String(255), nullable=False)
    City_ID = db.Column(db.Integer, db.ForeignKey('City.id'), nullable=False)
    Country_ID = db.Column(db.Integer, db.ForeignKey('Country.id'), nullable=False)
    Price = db.Column(db.Float, nullable=False)
    Available_From = db.Column(db.String(255), nullable=False)
    Available_To = db.Column(db.String(255), nullable=False)
    Owner_ID = db.Column(db.Integer, db.ForeignKey('Owner.id'), nullable=False)
    Lat = db.Column(db.String(255), nullable=False)
    Lng = db.Column(db.String(255), nullable=False)
    Kitchen = db.Column(db.Boolean, nullable=False)
    Breakfast = db.Column(db.Boolean, nullable=False)
    Breakfast_Lunch = db.Column(db.Boolean, nullable=False)
    Breakfast_Dinner = db.Column(db.Boolean, nullable=False)
    All_in = db.Column(db.Boolean, nullable=False)
    Bath = db.Column(db.Boolean, nullable=False)
    Balconies = db.Column(db.Boolean, nullable=False)
    Wi_Fi = db.Column(db.Boolean, nullable=False)
    Parking = db.Column(db.Boolean, nullable=False)

    def __init__(self, Name, Description, Address, City_ID, Country_ID, Price, Available_From, Available_To, Owner_ID,
                 Lat, Lng, Kitchen, Breakfast, Breakfast_Lunch, Breakfast_Dinner, All_in, Bath, Balconies, Wi_Fi,
                 Parking):
        self.Name = Name
        self.Description = Description
        self.Address = Address
        self.City_ID = City_ID
        self.Country_ID = Country_ID
        self.Price = Price
        self.Available_From = Available_From
        self.Available_To = Available_To
        self.Owner_ID = Owner_ID
        self.Lat = Lat
        self.Lng = Lng
        self.Kitchen = Kitchen
        self.Breakfast = Breakfast
        self.Breakfast_Lunch = Breakfast_Lunch
        self.Breakfast_Dinner = Breakfast_Dinner
        self.All_in = All_in
        self.Bath = Bath
        self.Balconies = Balconies
        self.Wi_Fi = Wi_Fi
        self.Parking = Parking


# Модель Review
class Review(db.Model):
    __tablename__ = 'Review'

    ID = db.Column(db.Integer, primary_key=True)
    User_ID = db.Column(db.Integer, nullable=False)
    Rent_Prop_ID = db.Column(db.Integer, db.ForeignKey('Rental_Property.ID'), nullable=True)
    Rating = db.Column(db.Integer)
    Comment = db.Column(db.String(500), nullable=True)

    rental_property = db.relationship("RentalProperty", backref="reviews")


class Comment(db.Model):
    __tablename__ = 'Comments'

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)
    review_id = db.Column(db.Integer, db.ForeignKey('Review.ID'), nullable=True)
    date = db.Column(db.Date)

    def __init__(self, comment, review_id, date):
        self.comment = comment
        self.review_id = review_id
        self.date = date


# Модель таблиці bookings
class Booking(db.Model):
    __tablename__ = 'Booking'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.ID'), nullable=False)
    rental_property_id = db.Column(db.Integer, db.ForeignKey('Rental_Property.ID'), nullable=False)
    check_in_date = db.Column(db.String(10), nullable=False)
    check_out_date = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __init__(self, user_id, rental_property_id, check_in_date, check_out_date, price):
        self.user_id = user_id
        self.rental_property_id = rental_property_id
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.price = price


class User(db.Model):
    __tablename__ = 'User'

    ID = db.Column(db.Integer, primary_key=True)
    First_Name = db.Column(db.String(50), nullable=False)
    Last_Name = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    Password = db.Column(db.String(100), nullable=False)
    Country = db.Column(db.String(50), nullable=False)
    rental_property_id = db.Column(db.Integer, db.ForeignKey('Rental_Property.ID'), nullable=False)

    def __repr__(self):
        return f'<User {self.Email}>'


# Клас моделі для таблиці Payment
class Payment(db.Model):
    __tablename__ = 'Payment'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.ID'), nullable=False)
    rental_property_id = db.Column(db.Integer, db.ForeignKey('Rental_Property.ID'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('Booking.id'), nullable=False)
    payment_date = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def __init__(self, user_id, rental_property_id, booking_id, payment_date, amount):
        self.user_id = user_id
        self.rental_property_id = rental_property_id
        self.booking_id = booking_id
        self.payment_date = payment_date
        self.amount = amount


# Модель таблиці "Images"
class Image(db.Model):
    _tablename__ = 'Image'

    id = db.Column(db.Integer, primary_key=True)
    rental_property_id = db.Column(db.Integer, db.ForeignKey('Rental_Property.ID'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Image id={self.id} rental_property_id={self.rental_property_id} image_path={self.image_path}>"


@app.route('/home')
def index():
    return "Hello, User!"

@app.route('/')
def index1():
    return "Hello, User!"


# Створення нової країни
@app.route('/countries', methods=['POST'])
def create_country():
    data = request.json
    country = Country(name=data['name'])
    db.session.add(country)
    db.session.commit()

    return 'Country created successfully', 201


@app.route('/countries/populate', methods=['POST'])
def populate_countries():
    data = pd.read_csv('output1.csv')  # Замініть 'countries.csv' на шлях до вашого CSV-файлу
    countries = []

    for index, row in data.iterrows():
        country = Country(name=row['Country'])
        countries.append(country)

    db.session.add_all(countries)
    db.session.commit()

    return 'Countries populated successfully', 201


# Отримання всіх країн
@app.route('/countries', methods=['GET'])
def get_all_countries():
    countries = Country.query.all()
    countries_list = []
    for country in countries:
        countries_list.append({'id': country.id, 'name': country.name})
    return jsonify({'countries': countries_list})


# Отримання однієї країни за її ID
@app.route('/countries/<int:country_id>', methods=['GET'])
def get_country(country_id):
    country = Country.query.get(country_id)
    if country:
        return jsonify({'country': country.name})
    else:
        return 'Country not found', 404


# Оновлення країни за її ID
@app.route('/countries/<int:country_id>', methods=['PUT'])
def update_country(country_id):
    data = request.json
    country = Country.query.get(country_id)
    if country:
        country.name = data['name']
        db.session.commit()
        return 'Country updated successfully'
    else:
        return 'Country not found', 404


# Видалення країни за її ID
@app.route('/countries/<int:country_id>', methods=['DELETE'])
def delete_country(country_id):
    country = Country.query.get(country_id)
    if country:
        db.session.delete(country)
        db.session.commit()
        return 'Country deleted successfully'
    else:
        return 'Country not found', 404


# Створення нового міста
@app.route('/cities', methods=['POST'])
def create_city():
    data = request.json
    city = City(name=data['name'], country_id=data['country_id'])
    db.session.add(city)
    db.session.commit()

    return 'City created successfully', 201


@app.route('/cities/populate', methods=['POST'])
def populate_cities():
    data = pd.read_csv('output1.csv')  # Замініть 'cities.csv' на шлях до вашого CSV-файлу
    cities = []

    for index, row in data.iterrows():
        city = City(name=row['city'], country_id=row['country'])
        cities.append(city)

    db.session.add_all(cities)
    db.session.commit()

    return 'Cities populated successfully', 201


# Отримання всіх міст
@app.route('/cities', methods=['GET'])
def get_all_cities():
    cities = City.query.all()
    cities_list = []
    for city in cities:
        cities_list.append({'id': city.id, 'name': city.name, 'country_id': city.country_id})
    return jsonify({'cities': cities_list})


# Отримання одного міста за його ID
@app.route('/cities/<int:city_id>', methods=['GET'])
def get_city(city_id):
    city = City.query.get(city_id)
    if city:
        return jsonify({'id': city.id, 'name': city.name, 'country_id': city.country_id})
    else:
        return 'City not found', 404


# Оновлення міста за його ID
@app.route('/cities/<int:city_id>', methods=['PUT'])
def update_city(city_id):
    data = request.json
    city = City.query.get(city_id)
    if city:
        city.name = data['name']
        city.country_id = data['country_id']
        db.session.commit()
        return 'City updated successfully'
    else:
        return 'City not found', 404


# Видалення міста за його ID
@app.route('/cities/<int:city_id>', methods=['DELETE'])
def delete_city(city_id):
    city = City.query.get(city_id)
    if city:
        db.session.delete(city)
        db.session.commit()
        return 'City deleted successfully'
    else:
        return 'City not found', 404


@app.route('/owners', methods=['POST'])
def create_owner():
    with app.app_context():
        first_name = request.json['first_name']
        last_name = request.json['last_name']
        email = request.json['email']
        password = request.json['password']
        country = request.json['country']

        new_owner = Owner(first_name=first_name, last_name=last_name, email=email, password=password, country=country)
        db.session.add(new_owner)
        db.session.commit()

        return jsonify({'message': 'Owner created successfully'})


@app.route('/owners', methods=['GET'])
def get_owners():
    owners = Owner.query.all()
    result = []
    for owner in owners:
        owner_data = {
            'id': owner.id,
            'first_name': owner.first_name,
            'last_name': owner.last_name,
            'email': owner.email,
            'password': owner.password,
            'country': owner.country
        }
        result.append(owner_data)
    return jsonify({'owners': result})


@app.route('/owners/<id>', methods=['GET'])
def get_owner(id):
    owner = Owner.query.get(id)
    if owner is None:
        return jsonify({'message': 'Owner not found'}), 404

    owner_data = {
        'id': owner.id,
        'first_name': owner.first_name,
        'last_name': owner.last_name,
        'email': owner.email,
        'password': owner.password,
        'country': owner.country
    }

    return jsonify(owner_data)


@app.route('/owners/<id>', methods=['PUT'])
def update_owner(id):
    owner = Owner.query.get(id)
    if owner is None:
        return jsonify({'message': 'Owner not found'}), 404

    owner.first_name = request.json['first_name']
    owner.last_name = request.json['last_name']
    owner.email = request.json['email']
    owner.password = request.json['password']
    owner.country = request.json['country']

    db.session.commit()

    return jsonify({'message': 'Owner updated successfully'})


@app.route('/owners/<id>', methods=['DELETE'])
def delete_owner(id):
    owner = Owner.query.get(id)
    if owner is None:
        return jsonify({'message': 'Owner not found'}), 404

    db.session.delete(owner)
    db.session.commit()

    return jsonify({'message': 'Owner deleted successfully'})


# Create a new Rental Property
@app.route('/rental_properties', methods=['POST'])
def create_rental_property():
    data = request.get_json()

    if 'City_ID' not in data or 'Country_ID' not in data or 'Owner_ID' not in data:
        abort(400, 'Missing required fields')

    City_ID = data['City_ID']
    Country_ID = data['Country_ID']
    Owner_ID = data['Owner_ID']

    if not City_ID or not isinstance(City_ID, int):
        abort(400, 'Invalid City ID')

    if not Country_ID or not isinstance(Country_ID, int):
        abort(400, 'Invalid Country ID')

    if not Owner_ID or not isinstance(Owner_ID, int):
        abort(400, 'Invalid Owner ID')

    # Перевірка існування власника з вказаним Owner_ID
    owner = Owner.query.get(Owner_ID)
    if not owner:
        abort(404, 'Owner not found')

    new_rental_property = RentalProperty(
        Name=data['Name'],
        Description=data['Description'],
        Address=data['Address'],
        City_ID=City_ID,
        Country_ID=Country_ID,
        Price=data['Price'],
        Available_From=data['Available_From'],
        Available_To=data['Available_To'],
        Owner_ID=Owner_ID,
        Lat=data['Lat'],
        Lng=data['Lng'],
        Kitchen=data['Kitchen'],
        Breakfast=data['Breakfast'],
        Breakfast_Lunch=data['Breakfast_Lunch'],
        Breakfast_Dinner=data['Breakfast_Dinner'],
        All_in=data['All_in'],
        Bath=data['Bath'],
        Balconies=data['Balconies'],
        Wi_Fi=data['Wi_Fi'],
        Parking=data['Parking']
    )
    db.session.add(new_rental_property)
    db.session.commit()

    return jsonify({'message': 'Rental Property created successfully', 'ID': new_rental_property.ID}), 201


# Get all Rental Properties
@app.route('/rental_properties', methods=['GET'])
def get_all_rental_properties():
    rental_properties = RentalProperty.query.all()
    result = []
    for rental_property in rental_properties:
        rental_property_data = {
            'ID': rental_property.ID,
            'Name': rental_property.Name,
            'Description': rental_property.Description,
            'Address': rental_property.Address,
            'City_ID': rental_property.City_ID,
            'Country_ID': rental_property.Country_ID,
            'Price': rental_property.Price,
            'Available_From': rental_property.Available_From,
            'Available_To': rental_property.Available_To,
            'Owner_ID': rental_property.Owner_ID,
            'Lat': rental_property.Lat,
            'Lng': rental_property.Lng,
            'Kitchen': rental_property.Kitchen,
            'Breakfast': rental_property.Breakfast,
            'Breakfast_Lunch': rental_property.Breakfast_Lunch,
            'Breakfast_Dinner': rental_property.Breakfast_Dinner,
            'All_in': rental_property.All_in,
            'Bath': rental_property.Bath,
            'Balconies': rental_property.Balconies,
            'Wi_Fi': rental_property.Wi_Fi,
            'Parking': rental_property.Parking
        }
        result.append(rental_property_data)
    return jsonify({'rental_properties': result}), 200


# Get a specific Rental Property by ID
@app.route('/rental_properties/<int:id>', methods=['GET'])
def get_rental_property(id):
    rental_property = RentalProperty.query.get(id)
    if rental_property:
        rental_property_data = {
            'ID': rental_property.ID,
            'Name': rental_property.Name,
            'Description': rental_property.Description,
            'Address': rental_property.Address,
            'City_ID': rental_property.City_ID,
            'Country_ID': rental_property.Country_ID,
            'Price': rental_property.Price,
            'Available_From': rental_property.Available_From,
            'Available_To': rental_property.Available_To,
            'Owner_ID': rental_property.Owner_ID,
            'Lat': rental_property.Lat,
            'Lng': rental_property.Lng,
            'Kitchen': rental_property.Kitchen,
            'Breakfast': rental_property.Breakfast,
            'Breakfast_Lunch': rental_property.Breakfast_Lunch,
            'Breakfast_Dinner': rental_property.Breakfast_Dinner,
            'All_in': rental_property.All_in,
            'Bath': rental_property.Bath,
            'Balconies': rental_property.Balconies,
            'Wi_Fi': rental_property.Wi_Fi,
            'Parking': rental_property.Parking
        }
        return jsonify({'rental_property': rental_property_data}), 200
    else:
        return jsonify({'message': 'Rental Property not found'}), 404


# Update a specific Rental Property by ID
@app.route('/rental_properties/<int:id>', methods=['PUT'])
def update_rental_property(id):
    rental_property = RentalProperty.query.get(id)
    if rental_property:
        data = request.json
        rental_property.Name = data['Name']
        rental_property.Description = data['Description']
        rental_property.Address = data['Address']
        rental_property.City_ID = data['City_ID']
        rental_property.Country_ID = data['Country_ID']
        rental_property.Price = data['Price']
        rental_property.Available_From = data['Available_From']
        rental_property.Available_To = data['Available_To']
        rental_property.Owner_ID = data['Owner_ID']
        rental_property.Lat = data['Lat']
        rental_property.Lng = data['Lng']
        rental_property.Kitchen = data['Kitchen']
        rental_property.Breakfast = data['Breakfast']
        rental_property.Breakfast_Lunch = data['Breakfast_Lunch']
        rental_property.Breakfast_Dinner = data['Breakfast_Dinner']
        rental_property.All_in = data['All_in']
        rental_property.Bath = data['Bath']
        rental_property.Balconies = data['Balconies']
        rental_property.Wi_Fi = data['Wi_Fi']
        rental_property.Parking = data['Parking']
        db.session.commit()
        return jsonify({'message': 'Rental Property updated successfully'}), 200
    else:
        return jsonify({'message': 'Rental Property not found'}), 404


# Delete a specific Rental Property by ID
@app.route('/rental_properties/<int:id>', methods=['DELETE'])
def delete_rental_property(id):
    rental_property = RentalProperty.query.get(id)
    if rental_property:
        db.session.delete(rental_property)
        db.session.commit()
        return jsonify({'message': 'Rental Property deleted successfully'}), 200
    else:
        return jsonify({'message': 'Rental Property not found'}), 404


@app.route('/login', methods=['GET', 'POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(Email=email).first()
    if user:
        if password == user.Password:
            # Generate JWT token
            expiration_time = datetime.datetime.utcnow() + datetime.timedelta(days=1)
            token = jwt.encode({
                'user_id': user.ID,
                'exp': expiration_time.isoformat()  # Token expiration time as string
            }, app.secret_key, algorithm='HS256')
            return jsonify({'message': 'Login successful', 'token': token}), 201


        else:
            print('Invalid email or password. Please try again.', 'error')
            return jsonify({'message': 'Invalid email or password'}), 401
    else:
        print('No user found with that email. Please sign up.', 'error')
        return jsonify({'message': 'User not found'}), 404


# Create a new User
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json

    if 'rental_property_id' not in data:
        abort(400, 'Missing rental_property_id')

    rental_property_id = data['rental_property_id']

    if not rental_property_id or not isinstance(rental_property_id, int):
        abort(400, 'Invalid rental_property_id')

    # Перевірка існування орендної власності з вказаним rental_property_id
    rental_property = RentalProperty.query.get(rental_property_id)
    if not rental_property:
        abort(404, 'Rental Property not found')

    new_user = User(
        First_Name=data['First_Name'],
        Last_Name=data['Last_Name'],
        Email=data['Email'],
        Password=data['Password'],
        Country=data['Country'],
        rental_property_id=rental_property_id
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully', 'ID': new_user.ID}), 201


# Get all Users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_data = []
    for user in users:
        user_data = {
            'ID': user.ID,
            'First_Name': user.First_Name,
            'Last_Name': user.Last_Name,
            'Email': user.Email,
            'Password': user.Password,
            'Country': user.Country,
            'rental_property_id': user.rental_property_id
        }
        users_data.append(user_data)
    return jsonify({'users': users_data}), 200


# Get a specific User by ID
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user:
        user_data = {
            'ID': user.ID,
            'First_Name': user.First_Name,
            'Last_Name': user.Last_Name,
            'Email': user.Email,
            'Password': user.Password,
            'Country': user.Country,
            'rental_property_id': user.rental_property_id
        }
        return jsonify({'user': user_data}), 200
    else:
        return jsonify({'message': 'User not found'}), 404


# Update a specific User by ID
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    if user:
        data = request.json
        user.First_Name = data['First_Name']
        user.Last_Name = data['Last_Name']
        user.Email = data['Email']
        user.Password = data['Password']
        user.Country = data['Country']
        user.rental_property_id = data['rental_property_id']
        db.session.commit()
        return jsonify({'message': 'User updated successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404


# Delete a specific User by ID
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404


# Отримати всі відгуки
@app.route('/reviews', methods=['GET'])
def get_reviews():
    reviews = Review.query.all()
    users_data = []
    for review in reviews:
        review_data = {
            'ID': review.ID,
            'User_ID': review.User_ID,
            'Rent_Prop_ID': review.Rent_Prop_ID,
            'Rating': review.Rating,
            'Comment': review.Comment
        }
        users_data.append(review_data)
    return jsonify({'users': users_data}), 200


# Отримати відгук за ID
@app.route('/reviews/<int:review_id>', methods=['GET'])
def get_review(review_id):
    review = Review.query.get(review_id)
    if review:
        review_data = {
            'ID': review.ID,
            'User_ID': review.User_ID,
            'Rent_Prop_ID': review.Rent_Prop_ID,
            'Rating': review.Rating,
            'Comment': review.Comment
        }
        return jsonify({'user': review_data}), 200
    else:
        return jsonify({'message': 'Review not found'}), 404


# Додати новий відгук
@app.route('/reviews', methods=['POST'])
def add_review():
    data = request.json
    user_id = data.get('user_id')
    rental_property_id = data.get('rental_property_id')
    rating = data.get('rating')
    comment = data.get('comment')

    # Перевірка наявності валідного rental_property_id
    rental_property = RentalProperty.query.get(rental_property_id)
    if rental_property is None:
        return jsonify({'error': 'Invalid rental_property_id'})

    # Перевірка наявності валідного user_id
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'error': 'Invalid user_id'})

    new_review = Review(User_ID=user_id, Rent_Prop_ID=rental_property_id, Rating=rating, Comment=comment)
    db.session.add(new_review)
    db.session.commit()

    return jsonify({'message': 'Review added successfully'})


# Оновити відгук за ID
@app.route('/reviews/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    review = Review.query.get(review_id)
    if review:
        data = request.json
        review.User_ID = data.get('User_ID', review.User_ID)
        review.Rent_Prop_ID = data.get('Rent_Prop_ID', review.Rent_Prop_ID)
        review.Rating = data.get('Rating', review.Rating)
        review.Comment = data.get('Comment', review.Comment)
        db.session.commit()
        return jsonify({'message': 'Review updated successfully'})
    else:
        return jsonify({'error': 'Review not found'}), 404


# Видалити відгук за ID
@app.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    review = Review.query.get(review_id)
    if review:
        db.session.delete(review)
        db.session.commit()
        return jsonify({'message': 'Review deleted successfully'})
    else:
        return jsonify({'error': 'Review not found'}), 404


@app.route('/bookings', methods=['POST'])
def create_booking():
    data = request.json
    user_id = data['user_id']
    rental_property_id = data['rental_property_id']
    check_in_date = data['check_in_date']
    check_out_date = data['check_out_date']
    price = data['price']

    # Check if rental_property_id and user_id are provided and valid
    if not rental_property_id or not isinstance(rental_property_id, int):
        return jsonify({'error': 'Invalid rental_property_id'})

    if not user_id or not isinstance(user_id, int):
        return jsonify({'error': 'Invalid user_id'})

    # Check if rental_property_id and user_id exist in the database
    rental_property = RentalProperty.query.get(rental_property_id)
    if not rental_property:
        return jsonify({'error': 'Rental Property not found'})

    # Create a new booking
    booking = Booking(user_id=user_id, rental_property_id=rental_property_id, check_in_date=check_in_date,
                      check_out_date=check_out_date, price=price)
    db.session.add(booking)
    db.session.commit()

    return jsonify({'message': 'Booking created successfully!'})


# Маршрут для отримання списку всіх бронювань
@app.route('/bookings', methods=['GET'])
def get_bookings():
    bookings = Booking.query.all()
    booking_list = []
    for booking in bookings:
        booking_data = {
            'id': booking.id,
            'user_id': booking.user_id,
            'rental_property_id': booking.rental_property_id,
            'check_in_date': booking.check_in_date,
            'check_out_date': booking.check_out_date,
            'price': booking.price
        }
        booking_list.append(booking_data)

    return jsonify({'bookings': booking_list})


# Маршрут для отримання деталей бронювання за ID
@app.route('/bookings/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if booking:
        booking_data = {
            'id': booking.id,
            'user_id': booking.user_id,
            'rental_property_id': booking.rental_property_id,
            'check_in_date': booking.check_in_date,
            'check_out_date': booking.check_out_date,
            'price': booking.price
        }
        return jsonify({'booking': booking_data})
    else:
        return jsonify({'message': 'Booking not found'}), 404


# Маршрут для оновлення деталей бронювання за ID
@app.route('/bookings/<int:booking_id>', methods=['PUT'])
def update_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if booking:
        data = request.json
        booking.user_id = data['user_id']
        booking.rental_property_id = data['rental_property_id']
        booking.check_in_date = data['check_in_date']
        booking.check_out_date = data['check_out_date']
        booking.price = data['price']
        db.session.commit()

        return jsonify({'message': 'Booking updated successfully!'})
    else:
        return jsonify({'message': 'Booking not found'}), 404


# Маршрут для видалення бронювання за ID
@app.route('/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if booking:
        db.session.delete(booking)
        db.session.commit()

        return jsonify({'message': 'Booking deleted successfully!'})
    else:
        return jsonify({'message': 'Booking not found'}), 404


# Маршрут для створення нового платежу
@app.route('/payments', methods=['POST'])
def create_payment():
    data = request.json
    rental_property_id = data.get('rental_property_id')
    booking_id = data.get('booking_id')
    user_id = data.get('user_id')
    payment_date = data.get('payment_date')
    amount = data.get('amount')

    # Validate rental_property_id
    rental_property = RentalProperty.query.get(rental_property_id)
    if not rental_property:
        return jsonify({'error': 'Invalid rental_property_id'})

    # Validate booking_id
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Invalid booking_id'})

    # Validate user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Invalid user_id'})

    new_payment = Payment(
        user_id=user_id,
        rental_property_id=rental_property_id,
        booking_id=booking_id,
        payment_date=payment_date,
        amount=amount
    )
    db.session.add(new_payment)
    db.session.commit()

    return jsonify({'message': 'Payment created successfully!'})


# Маршрут для отримання всіх платежів
@app.route('/payments', methods=['GET'])
def get_payments():
    payments = Payment.query.all()
    payment_list = []
    for payment in payments:
        payment_data = {
            'id': payment.id,
            'user_id': payment.user_id,
            'rental_property_id': payment.rental_property_id,
            'booking_id': payment.booking_id,
            'payment_date': payment.payment_date,
            'amount': payment.amount
        }
        payment_list.append(payment_data)

    return jsonify({'payments': payment_list})


# Маршрут для отримання деталей платежу за ID
@app.route('/payments/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    payment = Payment.query.get(payment_id)
    if payment:
        payment_data = {
            'id': payment.id,
            'user_id': payment.user_id,
            'rental_property_id': payment.rental_property_id,
            'booking_id': payment.booking_id,
            'payment_date': payment.payment_date,
            'amount': payment.amount
        }
        return jsonify({'payment': payment_data})
    else:
        return jsonify({'message': 'Payment not found'}), 404


# Маршрут для оновлення деталей платежу за ID
@app.route('/payments/<int:payment_id>', methods=['PUT'])
def update_payment(payment_id):
    payment = Payment.query.get(payment_id)
    if payment:
        data = request.json
        payment.user_id = data['user_id']
        payment.rental_property_id = data['rental_property_id']
        payment.booking_id = data['booking_id']
        payment.payment_date = data['payment_date']
        payment.amount = data['amount']
        db.session.commit()

        return jsonify({'message': 'Payment updated successfully!'})
    else:
        return jsonify({'message': 'Payment not found'}), 404


# Маршрут для видалення платежу за ID
@app.route('/payments/<int:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    payment = Payment.query.get(payment_id)
    if payment:
        db.session.delete(payment)
        db.session.commit()

        return jsonify({'message': 'Payment deleted successfully!'})
    else:
        return jsonify({'message': 'Payment not found'}), 404


# Маршрут для створення нового запису в таблиці "Images"
@app.route('/images', methods=['POST'])
def create_image():
    rental_property_id = request.form['rental_property_id']
    image_path = request.form['image_path']

    # Validate rental_property_id
    rental_property = RentalProperty.query.get(rental_property_id)
    if not rental_property:
        return jsonify({'error': 'Invalid rental_property_id'})

    image = Image(rental_property_id=rental_property_id, image_path=image_path)
    db.session.add(image)
    db.session.commit()

    return jsonify({'message': 'Image created successfully!'})


# Маршрут для отримання всіх записів з таблиці "Images"
@app.route('/images', methods=['GET'])
def get_all_images():
    images = Image.query.all()
    result = []
    for image in images:
        result.append({'id': image.id, 'rental_property_id': image.rental_property_id, 'image_path': image.image_path})
    return jsonify(result)


# Маршрут для отримання запису з таблиці "Images" за ID
@app.route('/images/<int:image_id>', methods=['GET'])
def get_image(image_id):
    image = Image.query.get(image_id)
    if image:
        return jsonify({'id': image.id, 'rental_property_id': image.rental_property_id, 'image_path': image.image_path})
    else:
        return jsonify({'message': 'Image not found'}), 404


# Маршрут для оновлення запису в таблиці "Images" за ID
@app.route('/images/<int:image_id>', methods=['PUT'])
def update_image(image_id):
    image = Image.query.get(image_id)
    if image:
        rental_property_id = request.form['rental_property_id']
        image_path = request.form['image_path']
        image.rental_property_id = rental_property_id
        image.image_path = image_path
        db.session.commit()
        return jsonify({'message': 'Image updated successfully!'})
    else:
        return jsonify({'message': 'Image not found'}), 404


# Маршрут для видалення запису з таблиці "Images" за ID
@app.route('/images/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    image = Image.query.get(image_id)
    if image:
        db.session.delete(image)
        db.session.commit()
        return jsonify({'message': 'Image deleted successfully!'})
    else:
        return jsonify({'message': 'Image not found'}), 404


if __name__ == '__main__':
    with app.app_context():  # Додано контекст додатку
        db.create_all()  # Створення бази даних
        app.run(debug=True)
