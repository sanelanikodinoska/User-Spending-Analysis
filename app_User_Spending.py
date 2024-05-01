import sqlite3
import pymongo
import json
import telegram
from telegram_credentials import *
from flask import Flask, request, jsonify


# Create Flask app

app = Flask(__name__)

# SQL database connection
def get_sqlite_connection():
    try: 
        connection = sqlite3.connect("C:/Users/user/Python developer/PYTHON developer_Project/users_vouchers.db")
        cursor = connection.cursor()
        return connection, cursor
    except Exception as e:
        return ({"error": str(e)}), 500

# MongoDB connection
def get_mongo_db():
    try: 
        client = pymongo.MongoClient('mongodb+srv://sanelatasnik:admin@learning.rsjglvl.mongodb.net/')
        db = client['users_vouchers']
        return db
    except Exception as e:
        return ({"error": str(e)}), 500

db = get_mongo_db()


# Telegram chat credentials
def get_telegram_bot():
    TOKEN = bot_token
    bot = telegram.Bot(token=TOKEN)
    return bot, TOKEN

bot = get_telegram_bot() 
TOKEN = get_telegram_bot() 


# Flask API Endpoints
@app.route('/')
def home_page():
    return 'Welcome to Sanela\'s first Python app'

# 1. Retrieve Total Spending by User 
@app.route('/total_spent/<int:user_id>')
def total_spent(user_id):
    # Retreive all user_ids from the SQL database table user_info 
    try: 
        connection, cursor = get_sqlite_connection()
        valid_user = '''
            SELECT user_id 
            FROM user_info
            ORDER BY user_id;
            '''
        cursor.execute(valid_user)
        result = cursor.fetchall()
                    
        if (user_id,) not in result:
            return jsonify ({"message": f"user {user_id} not found"}), 404

        # If user_id exists in the database, calculate the user total spending from table user_spending
        else: 
            query = '''
                    SELECT IFNULL(ROUND(SUM(money_spent),2),0) AS total_money_spent
                    FROM user_spending
                    WHERE user_id = ?;
                    '''
            cursor.execute(query, (user_id,))
            results = cursor.fetchone()
            connection.commit()
            connection.close()
            return jsonify ({"user_id": user_id, "total_spending": results[0]}), 200
    except Exception as e:
        return ({"error": str(e)}), 500
# 
# 
# # 2. Calculate Average Spending by Age Ranges    
@app.route('/average_spending_by_age')
def average_spending_by_age():
    try: 
        connection, cursor = get_sqlite_connection()
        query = '''
        SELECT 
            CASE 
            WHEN info.age >=18 AND info.age <=24 THEN "age 18 to 24"
            WHEN info.age >=25 AND info.age <=30 THEN "age 25 to 30"
            WHEN info.age >=31 AND info.age <=36 THEN "age 31 to 36"
            WHEN info.age >=37 AND info.age <=47 THEN "age 37 to 47"
            WHEN info.age > 47 THEN "older then 47"
            END AS age_range, 
            ROUND(AVG(spending.money_spent), 2) AS avg_money_spent_by_age_range
        FROM user_info AS info
        LEFT JOIN user_spending AS spending
        ON info.user_id = spending.user_id
        GROUP BY age_range
        ORDER BY age_range;
            '''
        cursor.execute(query)
        results = cursor.fetchall()
        connection.commit()
        connection.close()
        return dict(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
     
# 3. Write user data to MongoDB (spent above amount of 1000)
@app.route('/write_to_mongodb', methods = ['POST'])
def write_to_mongodb():
    request_data = json.loads(request.data)
    user_id = request_data.get("user_id")
    total_spending = request_data.get("total_spending")
    if not user_id or total_spending in request_data:
        return jsonify({"error": "both ('user_id' and 'total_spending') are required"}), 400    
    if total_spending > 1000:
        try: 
            vouchers_collection = db['vouchers']
            voucher_user = {
                "user_id": user_id,
                "total_spending" : total_spending
                }      
              
            user = vouchers_collection.find_one({"user_id": user_id})
            if not user:
                vouchers_collection.insert_one(voucher_user)
                return jsonify ({"message" : f"successfully added user {user_id} to vouchers_collection!"}), 201
            return jsonify ({"message":f"user {user_id} already in vouchers collection"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify ({"messsage": f"user {user_id} not eligible for getting voucher!"}), 200
    


# 4. Optional: Send statistical messages (average spendings by age range) to Telegram users
@app.route('/send_message_to_telegram', methods = ['POST'])
def send_message_to_telegram_users():
    try:
        telegram_msg = json.loads(request.data) 
        bot.sendMessage(chat_id = channel_id, text = telegram_msg)
        return jsonify({"message": "avg spendings successfully sent to telegram"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500   

# Handling app error
@app.errorhandler(404)
def error_occured(e):
    if e == 404:
        return 'Page does not exist', 404


#  Greeting API added
@app.route('/greeting/<name>')
def hello_name(name):
    return f"Hello {name}"


#  Starting the app
if __name__ == '__main__':
    app.run(debug = True)  
    # Flask app is now running
    # debug = True to be removed in production
    # if public, change the host parameter       
