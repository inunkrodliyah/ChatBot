from flask import Flask, render_template, request, jsonify
import json
import re
import random
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# 1. Inisialisasi Sastrawi secara Global
stemmer_factory = StemmerFactory()
stemmer = stemmer_factory.create_stemmer()

stopword_factory = StopWordRemoverFactory()
stopword_remover = stopword_factory.create_stop_word_remover()

# 2. Load Dataset Intents
with open('intents.json', 'r', encoding='utf-8') as file:
    intents_data = json.load(file)

# 3. Ekstraksi data latih (Gunakan text asli untuk menghindari timeout Vercel)
training_patterns = []
pattern_to_intent = []

for intent in intents_data['intents']:
    for pattern in intent['patterns']:
        # Mengubah ke lowercase dan membersihkan tanda baca ringan saja (sangat cepat)
        clean_pattern = pattern.lower().strip()
        clean_pattern = re.sub(r'[^\w\s]', '', clean_pattern)
        training_patterns.append(clean_pattern)
        pattern_to_intent.append(intent)

# 4. Fungsi Preprocessing khusus untuk Input User saja
def preprocess_user_input(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = stopword_remover.remove(text)
    text = stemmer.stem(text)
    return text

# 5. Vektorisasi menggunakan TF-IDF langsung dari text pola asli
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(training_patterns)

def chatbot_response(user_input):
    # Lakukan preprocessing Sastrawi secara real-time hanya pada 1 kalimat user ini
    cleaned_input = preprocess_user_input(user_input)
    if not cleaned_input.strip():
        return "Maaf, bisa tolong ketikkan pertanyaan yang lebih jelas?"

    # Transformasi input ke format TF-IDF
    user_vector = vectorizer.transform([cleaned_input])

    # Hitung Cosine Similarity
    similarity = cosine_similarity(user_vector, tfidf_matrix)
    best_match_idx = similarity.argmax()
    score = similarity[0][best_match_idx]

    # Batas ambang kecocokan (Threshold)
    if score > 0.15: # Menurunkan sedikit threshold karena data latih tidak di-stemming penuh
        matched_intent = pattern_to_intent[best_match_idx]
        return random.choice(matched_intent['responses'])
    else:
        return "Maaf, saya belum memahami pertanyaan tersebut. Coba tanyakan istilah lain seputar kampus UNAIR seperti Jalur PMB, ELPT, Cyber Campus, atau KRS."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    message = request.json.get('message', '')
    response = chatbot_response(message)
    return jsonify({'response': response})

# Handler port dinamis
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)