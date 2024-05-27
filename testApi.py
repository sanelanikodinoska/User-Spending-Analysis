import unittest
import json
from app_User_Spending import app

# Specific unit tests for API's endpoints to test all possible use-cases

class Test_app_User_Spending(unittest.TestCase):
    def setUp(self):
        self.app= app.test_client()

# Test for home page 
# @app.route('/')
    def test_home_page(self):
        responce = self.app.get('/')
        self.assertEqual(responce.status_code, 200)
        self.assertEqual(responce.data, b"Welcome to Sanela\'s first Python app")  

# Tests for retrieving Total Spending by User 
# @app.route('/total_spent/<int:user_id>')
    def test_total_spent_zero(self):
        responce = self.app.get('/total_spent/2')
        self.assertEqual(responce.status_code, 200)
        self.assertEqual(responce.data, b'{"total_spending":0,"user_id":2}\n')
            
    def test_total_spent_value(self):
        responce = self.app.get('/total_spent/100')
        self.assertEqual(responce.status_code, 200)
        self.assertEqual(responce.data, b'{"total_spending":20779.95,"user_id":100}\n')

    def test_total_spent_wrong_user(self):
        responce = self.app.get('/total_spent/5000')
        self.assertEqual(responce.status_code, 404)
        self.assertEqual(responce.data, b'{"message":"user 5000 not found"}\n')

# Tests for retrieving Average Spending by Age Ranges  
# @app.route('/average_spending_by_age')
    def test_average_spending_by_age(self):
        responce = self.app.get('/average_spending_by_age')
        self.assertEqual(responce.status_code, 200)
        self.assertEqual(responce.data, b'''{"age 18 to 24":2509.74,"age 25 to 30":2471.58,"age 31 to 36":2529.15,"age 37 to 47":2495.84,"older then 47":2485.77}\n''')                      
                 

#  Tests for writing user data to MongoDB 
# @app.route('/write_to_mongodb', methods = ['POST'])
# if user spending > 0
    def test_write_to_mongodb(self):
        post_data={"user_id": 405,"total_spending": 31063.57}
        responce = self.app.post('/write_to_mongodb', json = post_data)
        self.assertEqual(responce.status_code, 201)
        result = json.loads(responce.data)
        self.assertEqual(result, {"message" : "successfully added user 405 to vouchers_collection!"})

# if user spending = 0
    def test_not_eligible_for_mongodb(self):
        post_data={"user_id": 1,"total_spending": 0}
        responce = self.app.post('/write_to_mongodb', json=post_data)
        self.assertEqual(responce.status_code, 200)
        result = json.loads(responce.data)
        self.assertEqual(result, {"messsage": "user 1 not eligible for getting voucher!"})

# if user is already in MongoDB database (removing duplicates)

    def test_already_in_mongodb(self):
        post_data={"user_id": 400,"total_spending": 20049.29}
        responce = self.app.post('/write_to_mongodb', json=post_data)
        self.assertEqual(responce.status_code, 200)
        result = json.loads(responce.data)
        self.assertEqual(result, {"message": "user 400 already in vouchers collection"})

# if parametars user_id and total_spending are not provided
    def test_no_data_to_mongodb(self):
        post_data={}
        responce = self.app.post('/write_to_mongodb', json=post_data)
        self.assertEqual(responce.status_code, 400)
        result = json.loads(responce.data)
        self.assertEqual(result, {'error': "both ('user_id' and 'total_spending') are required"})


# Tests for sending statistical messages to Telegram  
# @app.route('/send_message_to_telegram', methods = ['POST'])) 
    def send_messages_to_telegram(self):
        post_data={'age 18 to 24': 2509.74, 'age 25 to 30': 2471.58, 'age 31 to 36': 2529.15, 'age 37 to 47': 2495.84, 'older then 47': 2485.77}
        
        responce = self.app.post('/send_message_to_telegram', json=post_data, bot = 'your_bot', chat_id = 'some_number')
        self.assertEqual(responce.status_code, 200)
        result = json.loads(responce.data)
        self.assertEqual(result, {'age 18 to 24': 2509.74, 'age 25 to 30': 2471.58, 'age 31 to 36': 2529.15, 'age 37 to 47': 2495.84, 'older then 47': 2485.77} )


# Run the tests
if __name__ == "__main__":
    unittest.main()

