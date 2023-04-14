import sqlite3

# Створення підключення до бази даних
conn = sqlite3.connect('accommodation.db')
cursor = conn.cursor()

# Створення таблиці приміщень
cursor.execute("""
CREATE TABLE IF NOT EXISTS premises (
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL,
    rooms INTEGER NOT NULL,
    price REAL NOT NULL,
    rating REAL, 
    max_occupancy INTEGER,
    additional_info TEXT
)
""")

# Створення таблиці країн
cursor.execute("""
CREATE TABLE IF NOT EXISTS countries (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
)
""")

# Створення таблиці міст
cursor.execute("""
CREATE TABLE IF NOT EXISTS cities (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    country_id INTEGER NOT NULL,
    FOREIGN KEY (country_id) REFERENCES countries (id)
)
""")

# SQL запит для створення таблиці Owner
create_owner_table = """
CREATE TABLE IF NOT EXISTS Owner (
    ID INTEGER PRIMARY KEY,
    First_Name TEXT NOT NULL,
    Last_Name TEXT NOT NULL,
    Email TEXT NOT NULL UNIQUE,
    Password TEXT NOT NULL,
    Country TEXT NOT NULL,
    FOREIGN KEY (Country) REFERENCES countries (name)
)
"""

cursor.execute("""
CREATE TABLE IF NOT EXISTS Rental_Property (
    ID INTEGER PRIMARY KEY,
    Name TEXT NOT NULL,
    Description TEXT,
    Address TEXT NOT NULL,
    City_ID INTEGER NOT NULL,
    Country_ID INTEGER NOT NULL,
    Price REAL NOT NULL,
    Available_From DATE NOT NULL,
    Available_To DATE NOT NULL,
    Owner_ID INTEGER NOT NULL,
    Lat TEXT NOT NULL,
    Lng TEXT NOT NULL,
    FOREIGN KEY (City_ID) REFERENCES Cities(ID),
    FOREIGN KEY (Country_ID) REFERENCES Countries(ID),
    FOREIGN KEY (Owner_ID) REFERENCES Owner(ID)
)
""")

# Створюємо таблицю User
cursor.execute("""
CREATE TABLE IF NOT EXISTS User (
    ID INTEGER PRIMARY KEY,
    First_Name TEXT NOT NULL,
    Last_Name TEXT NOT NULL,
    Email TEXT NOT NULL UNIQUE,
    Password TEXT NOT NULL,
    Country TEXT NOT NULL,
    rental_property_id INTEGER,
    FOREIGN KEY (rental_property_id) REFERENCES Rental_Property (ID)
)
""")

# Створення таблиці Review
cursor.execute("""
CREATE TABLE IF NOT EXISTS Review (
    ID INTEGER PRIMARY KEY,
    User_ID INTEGER NOT NULL,
    Rent_Prop_ID INTEGER NOT NULL,
    Rating INTEGER,
    Comment TEXT,
    FOREIGN KEY (User_ID) REFERENCES User (ID),
    FOREIGN KEY (Rent_Prop_ID) REFERENCES Rental_Property (ID)
)
""")

# Створюємо таблицю бронювань, якщо її ще не існує
cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    rental_property_id INTEGER NOT NULL,
    check_in_date TEXT NOT NULL,
    check_out_date TEXT NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (rental_property_id) REFERENCES rental_properties (id)
)
""")

# Створюємо таблицю Payment, якщо її ще не існує
cursor.execute("""
CREATE TABLE IF NOT EXISTS Payment (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    rental_property_id INTEGER NOT NULL,
    booking_id INTEGER NOT NULL,
    payment_date TEXT NOT NULL,
    amount REAL NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (rental_property_id) REFERENCES rental_properties (id),
    FOREIGN KEY (booking_id) REFERENCES bookings (id)
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS Images (
    ID INTEGER PRIMARY KEY,
    ID_Rental_Property INTEGER NOT NULL,
    Image_Path TEXT NOT NULL,
    FOREIGN KEY (ID_Rental_Property) REFERENCES Rental_Property(ID)
)
""")

# Збереження змін та закриття підключення
conn.commit()
conn.close()


def fetch_all_owners():
    cursor.execute("SELECT * FROM Owner")
    rows = cursor.fetchall()
    print("Власники:")
    print("ID | Ім'я | Прізвище | Email | Пароль | Країна")
    for row in rows:
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}")


def fetch_all_premises():
    cursor.execute("SELECT * FROM premises")
    rows = cursor.fetchall()
    print("Приміщення:")
    print("ID | Тип | Кімнати | Ціна | Рейтинг | Кількість людей | Додаткова інформація")
    for row in rows:
        print(
            f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]}")  # Додайте {row[4]} для rating та {row[5]} для min_rating


def fetch_all_countries():
    cursor.execute("SELECT * FROM countries")
    rows = cursor.fetchall()
    print("Країни:")
    print("ID | Назва")
    for row in rows:
        print(f"{row[0]} | {row[1]}")


def fetch_all_reviews():
    cursor.execute("""
    SELECT Review.ID, User.First_Name, User.Last_Name, Rental_Property.Name, Review.Rating, Review.Comment
    FROM Review
    INNER JOIN User ON Review.User_ID = User.ID
    INNER JOIN Rental_Property ON Review.Rent_Prop_ID = Rental_Property.ID
    """)
    rows = cursor.fetchall()
    print("Відгуки:")
    print("ID | Користувач | Об'єкт оренди | Рейтинг | Коментар")
    for row in rows:
        print(f"{row[0]} | {row[1]} {row[2]} | {row[3]} | {row[4]} | {row[5]}")


def fetch_all_cities():
    cursor.execute("SELECT * FROM cities")
    rows = cursor.fetchall()
    print("Міста:")
    print("ID | Назва | ID країни")
    for row in rows:
        print(f"{row[0]} | {row[1]} | {row[2]}")


def fetch_all_users():
    cursor.execute("SELECT * FROM User")
    rows = cursor.fetchall()
    print("Користувачі:")
    print("ID | First_Name | Last_Name | Email | Password | Country | rental_property_id")
    for row in rows:
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]}")


def fetch_all_rental_properties():
    cursor.execute("""
        SELECT rp.ID, rp.Name, rp.Description, rp.Address, c.Name AS City, co.Name AS Country, rp.Price, rp.Available_From, rp.Available_To, o.First_Name || ' ' || o.Last_Name AS Owner
        FROM Rental_Property rp
        INNER JOIN Cities c ON rp.City_ID = c.ID
        INNER JOIN Countries co ON rp.Country_ID = co.ID
        INNER JOIN Owner o ON rp.Owner_ID = o.ID
    """)
    rows = cursor.fetchall()
    print("Rental Properties:")
    print("ID | Name | Description | Address | City | Country | Price | Available_From | Available_To | Owner | Lat | Lng")
    for row in rows:
        print(
            f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]} | {row[8]} | {row[9]} | {[row[10]]} | {row[11]}")


def fetch_all_bookings():
    cursor.execute("SELECT * FROM bookings")
    rows = cursor.fetchall()
    print("Бронювання:")
    print("ID | ID користувача | ID орендованої властивості | Дата заселення | Дата виселення | Ціна")
    for row in rows:
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}")


def fetch_all_payments():
    # Вибираємо всі записи з таблиці Payment
    cursor.execute("SELECT * FROM Payment")
    rows = cursor.fetchall()
    print("Плата:")
    # Виводимо заголовок таблиці
    print("ID | User ID | Rental Property ID | Booking ID | Payment Date | Amount")

    # Виводимо дані про кожен запис у таблиці
    for row in rows:
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}")


def fetch_all_images():
    # Виконання запиту на отримання даних з таблиці "Images"
    cursor.execute("SELECT * FROM Images")
    rows = cursor.fetchall()
    print("Images:")
    # Виводимо заголовок таблиці
    print("ID | Image Path | Rental Property ID")
    # Виведення отриманих даних
    for row in rows:
        print(f"{row[0]} | {row[1]} | {row[2]}")

# Створення підключення до бази даних
conn = sqlite3.connect('accommodation.db')
cursor = conn.cursor()


def search_premises(max_price=None):
    query = "SELECT * FROM premises"
    conditions = []

    if max_price is not None:
        conditions.append(f"price <= {max_price}")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cursor.execute(query)
    rows = cursor.fetchall()
    print("Результати пошуку:")
    print("ID | Тип | Кімнати | Ціна | Додаткова інформація")
    for row in rows:
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}")


if __name__ == '__main__':
    # Виклик функцій для виведення даних з таблиць
    fetch_all_premises()
    fetch_all_countries()
    fetch_all_cities()
    fetch_all_users()
    fetch_all_owners()
    fetch_all_rental_properties()
    fetch_all_bookings()
    fetch_all_payments()
    fetch_all_reviews()
    fetch_all_images()

    cursor.execute(create_owner_table)

    # Закриття підключення
    conn.close()
