from flask import Flask, render_template, request, jsonify
import json
import nltk

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)

# Load data FAQ
with open('intents.json', 'r', encoding='utf-8') as file:
    intents = json.load(file)

questions = [item['question'] for item in intents['data']]
answers = [item['answer'] for item in intents['data']]

# TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(questions)

def chatbot_response(user_input):
    
    user_vector = vectorizer.transform([user_input])

    similarity = cosine_similarity(
        user_vector,
        tfidf_matrix
    )

    best_match = similarity.argmax()
    score = similarity[0][best_match]

    if score > 0.2:
        return answers[best_match]
    else:
        return "Maaf, saya belum memahami pertanyaan tersebut."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    
    message = request.json['message']

    response = chatbot_response(message)

    return jsonify({
        'response': response
    })

if __name__ == '__main__':
    app.run(debug=True)