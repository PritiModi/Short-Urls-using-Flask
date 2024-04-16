from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import hashlib
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(255), nullable=False)
    hashed_url = db.Column(db.String(255), nullable=False, unique=True)
    clicks = db.Column(db.Integer, default=0)
    used = db.Column(db.Boolean, default=False)

# API :: /hash
# PURPOSE :: get hased_url of original url
# PAYLOAD :: {
    # "original_url": "https://example.com/page"
# }
@app.route('/hash', methods=['POST'])
def hash_url():
    data = request.json
    original_url = data.get('original_url')
    if not original_url:
        return jsonify({'error': 'Original URL is required'}), 400
    
    hashed_url = hashlib.sha256(original_url.encode()).hexdigest()
    existing_url = db.session.query(URL).filter_by(hashed_url=hashed_url).first()
    if existing_url:
        return jsonify({'hashed_url': existing_url.hashed_url}), 200
    
    new_url = URL(original_url=original_url, hashed_url=hashed_url)
    db.session.add(new_url)
    db.session.commit()
    return jsonify({'hashed_url': hashed_url}), 201


# API :: hashed_url
# PURPOSE :: to get original_url and their location
@app.route('/<hashed_url>', methods=['GET'])
def get_url(hashed_url):
    url = db.session.query(URL).filter_by(hashed_url=hashed_url).first()

    if not url:
        return jsonify({'error': 'URL not found or already used'}), 404
    
    return jsonify({'original_url': url.original_url,'Location': url.original_url}), 302

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
