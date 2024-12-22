from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime
import boto3


# Mock database
users = {}
app = Flask(__name__)

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')
data_table = dynamodb.Table("DiaLog_Data")

class UserClient:
    def __init__(self, user_id):
        self.user_id = user_id

    def query_by_date_range(self, data_type, start_date, end_date):
        try:
            response = data_table.query(
                KeyConditionExpression=(
                        Key('userid#datatype').eq(f'{self.user_id}#{data_type}') &
                        Key('date').between(start_date, end_date)
                ),
                ProjectionExpression="date, value", # only get date and value
                Limit = 500 # limit number of items per request
            )
            return response.get('Items', [])
        except Exception as e:
            print(f"Error querying data: {e}")
            return None

# Configure Flask-JWT and SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/db_name'  # Update with your PostgreSQL URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Update with a strong secret key

db = SQLAlchemy(app)
jwt = JWTManager(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  # Hash passwords in production
    gender = db.Column(db.String(10))
    birthdate = db.Column(db.String(20))
    country_of_residence = db.Column(db.String(50))
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    consent = db.Column(db.Boolean)

# Create the database tables
with app.app_context():
    db.create_all()

# User registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    required_fields = [
        'first_name', 'last_name', 'email', 'password', 'confirm_password',
        'gender', 'birthdate', 'country_of_residence', 'emergency_contact',
        'weight', 'height', 'consent'
    ]

    # Check if all required fields are present
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Ensure passwords match
    if data['password'] != data['confirm_password']:
        return jsonify({"error": "Passwords do not match."}), 400

    # Ensure consent is given
    if not data.get('consent', False):
        return jsonify({"error": "User must agree to terms and conditions."}), 400

    # Register user
    user_id = len(users) + 1
    users[user_id] = {
        "first_name": data['first_name'],
        "last_name": data['last_name'],
        "email": data['email'],
        "gender": data['gender'],
        "birthdate": data['birthdate'],
        "country_of_residence": data['country_of_residence'],
        "emergency_contact": data['emergency_contact'],
        "weight": data['weight'],
        "height": data['height']
    }
    return jsonify({"message": "User registered successfully!", "user_id": user_id}), 201

# User login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password required."}), 400

    user = User.query.filter_by(email=email).first()
    if user and user.password == password:  # Hash comparison in production
        access_token = create_access_token(identity=user.id)
        return jsonify({"message": "Login successful", "access_token": access_token}), 200

    return jsonify({"error": "Invalid credentials."}), 401

# Get all users
@app.route('/users', methods=['GET'])
def get_users():
    return jsonify({"users": users}), 200

# Get a specific user by ID
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = users.get(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify(user), 200

# Extract user data to a downloadable file
@app.route('/users/<int:user_id>/export', methods=['GET'])
def export_user(user_id):
    user = users.get(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    # Create a simple text representation of the user data
    user_data = "\n".join([f"{key}: {value}" for key, value in user.items()])

    # Save to file
    file_path = f"user_{user_id}_data.txt"
    with open(file_path, 'w') as f:
        f.write(user_data)

    return jsonify({"message": "User data exported successfully!", "file": file_path}), 200

@app.route('/graphs', methods=['GET'])
@jwt_required()
def gen_graph():
    data = request.json()
    start = data.get("start")
    end = data.get("end")

    current_user_id = get_jwt_identity()  # Extract user_id from the JWT
    user = UserClient(current_user_id)  # Create a User instance

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not start_date or not end_date:
        return jsonify({"error": "Missing required parameters"}), 400

    data = user.query_data(start_date, end_date)
    if data is None:
        return jsonify({"error": "Failed to query data"}), 500

    return jsonify({"data": data})

@app.route('/alert-doctor', methods=['POST'])
def send_alert(bloodSugarLevel):
    # messaging API
    pass

# send notifications accroding to user's personal settings


if __name__ == '__main__':
    app.run(debug=True)
