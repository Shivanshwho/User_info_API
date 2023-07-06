from flask import Flask, request, jsonify
import psycopg2
import requests
import json
app = Flask(__name__)
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'user_info'
DB_USER = 'postgres'
DB_PASSWORD = 'Ovd@0312'

def create_user_table():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id SERIAL PRIMARY KEY,
                  first_name TEXT,
                  last_name TEXT,
                  age INTEGER,
                  gender TEXT,
                  email TEXT,
                  phone TEXT,
                  birth_date DATE)''')
    conn.commit()
    conn.close()

create_user_table()


@app.route('/api/users')
def search_users():
    first_name = request.args.get('first_name')

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE first_name ILIKE %s", (first_name + '%',))
    result = c.fetchall()
    conn.close()

    if result:
        # Users found, return the list of matching users in a JSON response
        users = []
        for row in result:
            user = {
                'id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'age': row[3],
                'gender': row[4],
                'email': row[5],
                'phone': row[6],
                'birth_date': row[7].strftime('%Y-%m-%d')
            }
            users.append(user)
        return jsonify(users)
    else:
        # Users not found, call the dummy JSON API and save the resulting users to the user table
        dummy_api_url = 'https://dummyjson.com/users/search'
        params = {'q': first_name}
        response = requests.get(dummy_api_url, params=params)
        if response.status_code == 200:
            dummy_users = response.json()
           

            dummy_user_details = dummy_users['users']
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            
            c = conn.cursor()
            curr_output=[]
            for user in dummy_user_details:
                first_name = user['firstName']
                last_name = user['lastName']
                age = user['age']
                gender = user['gender']
                email = user['email']
                phone = user['phone']
                birth_date = user['birthDate']
                curr_output.append([first_name, last_name, age, gender, email, phone, birth_date])
                c.execute("INSERT INTO users (first_name, last_name, age, gender, email, phone, birth_date) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                          (first_name, last_name, age, gender, email, phone, birth_date))
            conn.commit()
            conn.close()

            return curr_output
        else:
            return jsonify({'error': 'Failed to fetch users from the dummy API'})

if __name__ == '__main__':
    app.run(debug=True)
