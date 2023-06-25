import datetime
import secrets
from flask import Flask, request, jsonify
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
    country_id = db.Column(db.Integer, db.ForeignKey('Country.id'), nullable=False)


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
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255))
    country = db.Column(db.String(255))
    price = db.Column(db.Float, nullable=False)
    available_from = db.Column(db.String(255))
    available_to = db.Column(db.String(255))
    owner_id = db.Column(db.Integer)
    room_prop_id = db.Column(db.Integer, db.ForeignKey('rental_prop_room_prop.id'))
    food_prop_id = db.Column(db.Integer, db.ForeignKey('sub_rental_prop_eat.id'))

    def __init__(self, name, description, address, city, country, price, available_from, available_to, owner_id,
                 room_prop_id, food_prop_id):
        self.name = name
        self.description = description
        self.address = address
        self.city = city
        self.country = country
        self.price = price
        self.available_from = available_from
        self.available_to = available_to
        self.owner_id = owner_id
        self.room_prop_id = room_prop_id
        self.food_prop_id = food_prop_id


class RentalPropRoomProp(db.Model):
    __tablename__ = 'rental_prop_room_prop'

    id = db.Column(db.Integer, primary_key=True)
    bath = db.Column(db.Boolean)
    balconies = db.Column(db.Boolean)
    wi_fi = db.Column(db.Boolean)
    parking = db.Column(db.Boolean)
    is_pets = db.Column(db.Boolean)
    is_tv = db.Column(db.Boolean)
    card_cash = db.Column(db.Boolean)

    def __init__(self, bath, balconies, wi_fi, parking, is_pets, is_tv, card_cash):
        self.bath = bath
        self.balconies = balconies
        self.wi_fi = wi_fi
        self.parking = parking
        self.is_pets = is_pets
        self.is_tv = is_tv
        self.card_cash = card_cash


class SubRentalPropEat(db.Model):
    __tablename__ = 'sub_rental_prop_eat'

    id = db.Column(db.Integer, primary_key=True)
    all_in = db.Column(db.Boolean)
    kitchen = db.Column(db.Boolean)
    breakfast = db.Column(db.Boolean)
    lunch = db.Column(db.Boolean)
    dinner = db.Column(db.Boolean)

    def __init__(self, all_in, kitchen, breakfast, lunch, dinner):
        self.all_in = all_in
        self.kitchen = kitchen
        self.breakfast = breakfast
        self.lunch = lunch
        self.dinner = dinner


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
    data = pd.read_csv('output.csv')  # Замініть 'cities.csv' на шлях до вашого CSV-файлу
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


# Декоратор для маршруту POST
@app.route('/rental_property', methods=['POST'])
def create_rental_property():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    address = data.get('address')
    city = data.get('city')
    country = data.get('country')
    price = data.get('price')
    available_from = data.get('available_from')
    available_to = data.get('available_to')
    owner_id = data.get('owner_id')
    room_prop_id = data.get('room_prop_id')
    food_prop_id = data.get('food_prop_id')

    rental_property = RentalProperty(name, description, address, city, country, price, available_from, available_to,
                                     owner_id, room_prop_id, food_prop_id)
    db.session.add(rental_property)
    db.session.commit()

    return jsonify({'message': 'Rental property created successfully'}), 201


# Декоратор для маршруту GET з id
@app.route('/rental_property/<int:rental_property_id>', methods=['GET'])
def get_rental_property(rental_property_id):
    rental_property = RentalProperty.query.get(rental_property_id)
    if not rental_property:
        return jsonify({'message': 'Rental property not found'}), 404

    rental_property_data = {
        'ID': rental_property.ID,
        'name': rental_property.name,
        'description': rental_property.description,
        'address': rental_property.address,
        'city': rental_property.city,
        'country': rental_property.country,
        'price': rental_property.price,
        'available_from': rental_property.available_from,
        'available_to': rental_property.available_to,
        'owner_id': rental_property.owner_id,
        'room_prop_id': rental_property.room_prop_id,
        'food_prop_id': rental_property.food_prop_id
    }

    return jsonify(rental_property_data), 200


# Декоратор для маршруту GET
@app.route('/rental_property', methods=['GET'])
def get_all_rental_properties():
    rental_properties = RentalProperty.query.all()

    rental_properties_data = []
    for rental_property in rental_properties:
        rental_property_data = {
            'ID': rental_property.ID,
            'name': rental_property.name,
            'description': rental_property.description,
            'address': rental_property.address,
            'city': rental_property.city,
            'country': rental_property.country,
            'price': rental_property.price,
            'available_from': rental_property.available_from,
            'available_to': rental_property.available_to,
            'owner_id': rental_property.owner_id,
            'room_prop_id': rental_property.room_prop_id,
            'food_prop_id': rental_property.food_prop_id
        }
        rental_properties_data.append(rental_property_data)

    return jsonify(rental_properties_data), 200


# Декоратор для маршруту PUT з id
@app.route('/rental_property/<int:rental_property_id>', methods=['PUT'])
def update_rental_property(rental_property_id):
    rental_property = RentalProperty.query.get(rental_property_id)
    if not rental_property:
        return jsonify({'message': 'Rental property not found'}), 404

    data = request.get_json()
    rental_property.name = data.get('name', rental_property.name)
    rental_property.description = data.get('description', rental_property.description)
    rental_property.address = data.get('address', rental_property.address)
    rental_property.city = data.get('city', rental_property.city)
    rental_property.country = data.get('country', rental_property.country)
    rental_property.price = data.get('price', rental_property.price)
    rental_property.available_from = data.get('available_from', rental_property.available_from)
    rental_property.available_to = data.get('available_to', rental_property.available_to)
    rental_property.owner_id = data.get('owner_id', rental_property.owner_id)
    rental_property.room_prop_id = data.get('room_prop_id', rental_property.room_prop_id)
    rental_property.food_prop_id = data.get('food_prop_id', rental_property.food_prop_id)

    db.session.commit()

    return jsonify({'message': 'Rental property updated successfully'}), 200


# Декоратор для маршруту DELETE з id
@app.route('/rental_property/<int:rental_property_id>', methods=['DELETE'])
def delete_rental_property(rental_property_id):
    rental_property = RentalProperty.query.get(rental_property_id)
    if not rental_property:
        return jsonify({'message': 'Rental property not found'}), 404

    db.session.delete(rental_property)
    db.session.commit()

    return jsonify({'message': 'Rental property deleted successfully'}), 200


@app.route('/rental_prop_room_prop', methods=['POST'])
def create_rental_prop_room_prop():
    data = request.get_json()

    bath = data['bath']
    balconies = data['balconies']
    wi_fi = data['wi_fi']
    parking = data['parking']
    is_pets = data['is_pets']
    is_tv = data['is_tv']
    card_cash = data['card_cash']

    room_prop = RentalPropRoomProp(
        bath=bath,
        balconies=balconies,
        wi_fi=wi_fi,
        parking=parking,
        is_pets=is_pets,
        is_tv=is_tv,
        card_cash=card_cash
    )

    db.session.add(room_prop)
    db.session.commit()

    return jsonify({'message': 'Rental property room properties created successfully'}), 201


@app.route('/rental_prop_room_prop', methods=['GET'])
def get_all_rental_prop_room_props():
    room_props = RentalPropRoomProp.query.all()

    result = []
    for room_prop in room_props:
        result.append({
            'id': room_prop.id,
            'bath': room_prop.bath,
            'balconies': room_prop.balconies,
            'wi_fi': room_prop.wi_fi,
            'parking': room_prop.parking,
            'is_pets': room_prop.is_pets,
            'is_tv': room_prop.is_tv,
            'card_cash': room_prop.card_cash
        })

    return jsonify({'room_properties': result}), 200


@app.route('/rental_prop_room_prop/<int:room_prop_id>', methods=['GET'])
def get_rental_prop_room_prop(room_prop_id):
    room_prop = RentalPropRoomProp.query.get(room_prop_id)
    if not room_prop:
        return jsonify({'message': 'Rental property room properties not found'}), 404

    return jsonify({
        'id': room_prop.id,
        'bath': room_prop.bath,
        'balconies': room_prop.balconies,
        'wi_fi': room_prop.wi_fi,
        'parking': room_prop.parking,
        'is_pets': room_prop.is_pets,
        'is_tv': room_prop.is_tv,
        'card_cash': room_prop.card_cash
    }), 200


# Декоратор для маршруту DELETE з id
@app.route('/rental_prop_room_prop/<int:rental_prop_room_prop_id>', methods=['DELETE'])
def delete_rental_prop_room_prop(rental_prop_room_prop_id):
    rental_prop_room_prop = RentalPropRoomProp.query.get(rental_prop_room_prop_id)
    if not rental_prop_room_prop:
        return jsonify({'message': 'Rental property room property not found'}), 404

    db.session.delete(rental_prop_room_prop)
    db.session.commit()

    return jsonify({'message': 'Rental property room property deleted successfully'}), 200


# Декоратор для маршруту PUT з id
@app.route('/rental_prop_room_prop/<int:rental_prop_room_prop_id>', methods=['PUT'])
def update_rental_prop_room_prop(rental_prop_room_prop_id):
    rental_prop_room_prop = RentalPropRoomProp.query.get(rental_prop_room_prop_id)
    if not rental_prop_room_prop:
        return jsonify({'message': 'Rental property room property not found'}), 404

    data = request.get_json()

    rental_prop_room_prop.bath = data.get('bath', rental_prop_room_prop.bath)
    rental_prop_room_prop.balconies = data.get('balconies', rental_prop_room_prop.balconies)
    rental_prop_room_prop.wi_fi = data.get('wi_fi', rental_prop_room_prop.wi_fi)
    rental_prop_room_prop.parking = data.get('parking', rental_prop_room_prop.parking)
    rental_prop_room_prop.is_pets = data.get('is_pets', rental_prop_room_prop.is_pets)
    rental_prop_room_prop.is_tv = data.get('is_tv', rental_prop_room_prop.is_tv)
    rental_prop_room_prop.card_cash = data.get('card_cash', rental_prop_room_prop.card_cash)

    db.session.commit()

    return jsonify({'message': 'Rental property room property updated successfully'}), 200


# Декоратор для маршруту POST
@app.route('/sub_rental_prop_eat', methods=['POST'])
def create_sub_rental_prop_eat():
    data = request.get_json()

    all_in = data['all_in']
    kitchen = data['kitchen']
    breakfast = data['breakfast']
    lunch = data['lunch']
    dinner = data['dinner']

    sub_rental_prop_eat = SubRentalPropEat(
        all_in=all_in,
        kitchen=kitchen,
        breakfast=breakfast,
        lunch=lunch,
        dinner=dinner
    )

    db.session.add(sub_rental_prop_eat)
    db.session.commit()

    return jsonify({'message': 'Sub rental property eat properties created successfully'}), 201


# Декоратор для маршруту GET без id
@app.route('/sub_rental_prop_eat', methods=['GET'])
def get_all_sub_rental_prop_eat():
    sub_rental_prop_eats = SubRentalPropEat.query.all()

    result = []
    for sub_rental_prop_eat in sub_rental_prop_eats:
        result.append({
            'id': sub_rental_prop_eat.id,
            'all_in': sub_rental_prop_eat.all_in,
            'kitchen': sub_rental_prop_eat.kitchen,
            'breakfast': sub_rental_prop_eat.breakfast,
            'lunch': sub_rental_prop_eat.lunch,
            'dinner': sub_rental_prop_eat.dinner
        })

    return jsonify({'sub_rental_prop_eats': result}), 200


# Декоратор для маршруту GET з id
@app.route('/sub_rental_prop_eat/<int:sub_rental_prop_eat_id>', methods=['GET'])
def get_sub_rental_prop_eat(sub_rental_prop_eat_id):
    sub_rental_prop_eat = SubRentalPropEat.query.get(sub_rental_prop_eat_id)
    if not sub_rental_prop_eat:
        return jsonify({'message': 'Sub rental property eat properties not found'}), 404

    return jsonify({
        'id': sub_rental_prop_eat.id,
        'all_in': sub_rental_prop_eat.all_in,
        'kitchen': sub_rental_prop_eat.kitchen,
        'breakfast': sub_rental_prop_eat.breakfast,
        'lunch': sub_rental_prop_eat.lunch,
        'dinner': sub_rental_prop_eat.dinner
    }), 200


# Декоратор для маршруту DELETE з id
@app.route('/sub_rental_prop_eat/<int:sub_rental_prop_eat_id>', methods=['DELETE'])
def delete_sub_rental_prop_eat(sub_rental_prop_eat_id):
    sub_rental_prop_eat = SubRentalPropEat.query.get(sub_rental_prop_eat_id)
    if not sub_rental_prop_eat:
        return jsonify({'message': 'Sub rental property eat not found'}), 404

    db.session.delete(sub_rental_prop_eat)
    db.session.commit()

    return jsonify({'message': 'Sub rental property eat deleted successfully'}), 200


# Декоратор для маршруту PUT з id
@app.route('/sub_rental_prop_eat/<int:sub_rental_prop_eat_id>', methods=['PUT'])
def update_sub_rental_prop_eat(sub_rental_prop_eat_id):
    sub_rental_prop_eat = SubRentalPropEat.query.get(sub_rental_prop_eat_id)
    if not sub_rental_prop_eat:
        return jsonify({'message': 'Sub rental property eat not found'}), 404

    data = request.get_json()

    sub_rental_prop_eat.all_in = data.get('all_in', sub_rental_prop_eat.all_in)
    sub_rental_prop_eat.kitchen = data.get('kitchen', sub_rental_prop_eat.kitchen)
    sub_rental_prop_eat.breakfast = data.get('breakfast', sub_rental_prop_eat.breakfast)
    sub_rental_prop_eat.lunch = data.get('lunch', sub_rental_prop_eat.lunch)
    sub_rental_prop_eat.dinner = data.get('dinner', sub_rental_prop_eat.dinner)

    db.session.commit()

    return jsonify({'message': 'Sub rental property eat updated successfully'}), 200


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

    new_user = User(
        First_Name=data['First_Name'],
        Last_Name=data['Last_Name'],
        Email=data['Email'],
        Password=data['Password'],
        Country=data['Country'],
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
