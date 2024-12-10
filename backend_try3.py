from flask import Flask, request, jsonify

app = Flask(__name__)

# Mock database
users = {}
logs = []

# User registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    user_id = len(users) + 1
    users[user_id] = data
    return jsonify({"message": "User registered successfully!", "user_id": user_id}), 201

# Add a log entry
@app.route('/logs', methods=['POST'])
def add_log():
    data = request.json
    log_id = len(logs) + 1
    logs.append({"id": log_id, **data})
    return jsonify({"message": "Log added successfully!", "log_id": log_id}), 201

# Fetch all log entries
@app.route('/logs', methods=['GET'])
def get_logs():
    return jsonify({"logs": logs}), 200

# Fetch a specific log entry
@app.route('/logs/<int:log_id>', methods=['GET'])
def get_log(log_id):
    log = next((log for log in logs if log["id"] == log_id), None)
    if log is None:
        return jsonify({"error": "Log not found"}), 404
    return jsonify(log), 200

if __name__ == '__main__':
    app.run(debug=True)
