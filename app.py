from flask import Flask, request, jsonify
import tensorflow as tf
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import scipy.sparse as sp
import joblib

app = Flask(__name__)

# Load the trained model
model = tf.keras.models.load_model('saved_models/cnn_lstm_model.h5')
vectorizer = joblib.load('saved_models/tfidf_vectorizer.pkl')

def preprocess_text(text):
    text = re.sub(r'[^\w\s]', '', text.lower())
    return text

@app.route('/predict', methods=['GET','POST'])
def predict():
    try:
        data = request.get_json(force=True)
        question1 = preprocess_text(data['question1'])
        question2 = preprocess_text(data['question2'])
    except (TypeError, KeyError) as e:
        return jsonify({"error": str(e), "message": "Invalid input data"}), 400

    q1_tfidf = vectorizer.transform([question1])
    q2_tfidf = vectorizer.transform([question2])
    X = sp.hstack((q1_tfidf, q2_tfidf))

    prediction = (model.predict(X) > 0.5).astype("int32")[0][0]

    return jsonify({'is_duplicate': int(prediction)})

@app.route('/')
def home():
    return "Welcome to the Duplicate Question Detection API. Use /predict endpoint with POST method."

if __name__ == '__main__':
    app.run(debug=True)
