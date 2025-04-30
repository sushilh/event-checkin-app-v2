
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import csv
import os

app = Flask(__name__, static_folder=".")
CORS(app)

CSV_FILE = 'attendees.csv'

def read_attendees():
    attendees = []
    try:
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                attendees.append(row)
    except FileNotFoundError:
        pass
    return attendees

def write_attendees(attendees):
    fieldnames = ['name', 'email', 'attendees', 'allergy', 'checked_in', 'checked_in_count']
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(attendees)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/attendees', methods=['GET'])
def get_attendees():
    return jsonify(read_attendees())

@app.route('/checkin', methods=['POST'])
def checkin_attendee():
    data = request.get_json()
    email = data.get('email')
    checked_in = data.get('checked_in', 'no')
    count = str(data.get('checked_in_count', '0'))

    attendees = read_attendees()
    for attendee in attendees:
        if attendee['email'].lower() == email.lower():
            attendee['checked_in'] = checked_in
            attendee['checked_in_count'] = count if checked_in == 'yes' else '0'
            break
    write_attendees(attendees)
    return jsonify({'message': 'Check-in status updated successfully.'})

@app.route('/attendees', methods=['PUT'])
def update_attendee():
    data = request.get_json()
    email = data.get('email')
    update_type = data.get('type')
    value = str(data.get('value', '0'))

    attendees = read_attendees()
    for attendee in attendees:
        if attendee['email'].lower() == email.lower():
            if update_type == 'attendees':
                attendee['attendees'] = value
            elif update_type == 'checked_in_count':
                attendee['checked_in_count'] = value
            break
    write_attendees(attendees)
    return jsonify({'message': f'{update_type} updated successfully.'})

@app.route('/add', methods=['POST'])
def add_guest():
    data = request.get_json()
    new_guest = {
        'name': data.get('name', ''),
        'email': data.get('email', ''),
        'attendees': str(data.get('attendees', 0)),
        'allergy': data.get('allergy', ''),
        'checked_in': data.get('checked_in', 'no'),
        'checked_in_count': '0'
    }
    attendees = read_attendees()
    attendees.append(new_guest)
    write_attendees(attendees)
    return jsonify({'message': 'Guest added successfully.'})

if __name__ == '__main__':
    app.run(debug=True)
