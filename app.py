from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, methods=['GET', 'POST', 'DELETE', 'OPTIONS', 'PATCH', 'PUT'])

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hotel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(50), nullable=False, unique=True)
    type = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Available')  # Explicitly set nullable=False

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guest_name = db.Column(db.String(100), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    room = db.relationship('Room', backref='bookings')

# Initialize database
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    rooms = Room.query.all()
    return render_template('index.html', rooms=rooms)

@app.route('/rooms', methods=['GET'])
def get_rooms():
    rooms = Room.query.all()
    return jsonify([{
        'id': r.id, 'number': r.number, 'type': r.type,
        'price': r.price, 'status': r.status
    } for r in rooms]), 200

@app.route('/rooms', methods=['POST'])
def add_room():
    data = request.get_json()  # Ensures JSON is parsed correctly
    if not data or not all(k in data for k in ['number', 'type', 'price']):
        return jsonify({'message': 'Missing required fields'}), 400

    new_room = Room(
        number=data['number'],
        type=data['type'],
        price=data['price'],
        status=data.get('status', 'Available')
    )
    
    db.session.add(new_room)
    db.session.commit()
    
    return jsonify({'message': 'Room added successfully'}), 201

@app.route('/bookings', methods=['POST'])
def add_booking():
    data = request.get_json()
    if not data or not all(k in data for k in ['guest_name', 'room_id', 'check_in', 'check_out']):
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        check_in_date = datetime.strptime(data['check_in'], '%Y-%m-%d').date()
        check_out_date = datetime.strptime(data['check_out'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format, use YYYY-MM-DD'}), 400

    if check_in_date >= check_out_date:
        return jsonify({'message': 'Check-out date must be after check-in date'}), 400

    room = Room.query.get(data['room_id'])
    if not room or room.status != 'Available':
        return jsonify({'message': 'Room not available'}), 400

    new_booking = Booking(
        guest_name=data['guest_name'],
        room_id=data['room_id'],
        check_in=check_in_date,
        check_out=check_out_date
    )
    
    room.status = 'Booked'
    
    db.session.add(new_booking)
    db.session.commit()
    
    return jsonify({'message': 'Booking successful'}), 201

@app.route('/bookings/<int:id>', methods=['DELETE'])
def cancel_booking(id):
    booking = Booking.query.get(id)
    if not booking:
        return jsonify({'message': 'Booking not found'}), 404

    room = Room.query.get(booking.room_id)
    if room:
        room.status = 'Available'

    db.session.delete(booking)
    db.session.commit()

    return jsonify({'message': 'Booking canceled successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
