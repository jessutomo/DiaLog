from flask import Flask, request, jsonify

app = Flask(__name__)

# Mock database
patient_conditions = {}

# Add or update diabetic condition data
@app.route('/conditions', methods=['POST'])
def add_conditions():
    data = request.json
    patient_id = data.get("patient_id")
    if not patient_id:
        return jsonify({"error": "Patient ID is required"}), 400
    
    # Add or update the patient's condition data
    patient_conditions[patient_id] = data
    return jsonify({"message": "Patient condition data saved successfully!", "patient_id": patient_id}), 201

# Get diabetic condition data for a specific patient
@app.route('/conditions/<patient_id>', methods=['GET'])
def get_conditions(patient_id):
    data = patient_conditions.get(patient_id)
    if not data:
        return jsonify({"error": "No data found for the specified patient ID"}), 404
    return jsonify(data), 200

# Fetch all patient condition data
@app.route('/conditions', methods=['GET'])
def get_all_conditions():
    return jsonify({"patients": patient_conditions}), 200

if __name__ == '__main__':
    app.run(debug=True)
