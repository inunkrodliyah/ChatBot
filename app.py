from flask import Flask, render_template, request, jsonify
import json
import re
import random
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# 1. Inisialisasi Sastrawi untuk Preprocessing Bahasa Indonesia
stemmer_factory = StemmerFactory()
stemmer = stemmer_factory.create_stemmer()

stopword_factory = StopWordRemoverFactory()
stopword_remover = stopword_factory.create_stop_word_remover()

# 2. Load Dataset Intents
with open('intents.json', 'r', encoding='utf-8') as file:
    intents_data = json.load(file)

# 3. Ekstraksi data untuk training TF-IDF
training_patterns = []
pattern_to_intent = []  # Menyimpan referensi intent dari setiap pattern

for intent in intents_data['intents']:
    for pattern in intent['patterns']:
        training_patterns.append(pattern)
        pattern_to_intent.append(intent)

# 4. Fungsi Preprocessing (Case Folding, Cleaning, Stopword, Stemming)
def preprocess_text(text):
    # Case Folding
    text = text.lower()
    # Cleaning (menghapus angka dan tanda baca)
    text = re.sub(r'[^\w\s]', '', text)
    # Stopword Removal
    text = stopword_remover.remove(text)
    # Stemming
    text = stemmer.stem(text)
    return text

# Preprocessing semua data latih di awal saat aplikasi berjalan
preprocessed_patterns = [preprocess_text(pattern) for pattern in training_patterns]

# 5. Vektorisasi menggunakan TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(preprocessed_patterns)

def chatbot_response(user_input):
    # Preprocessing input pengguna
    cleaned_input = preprocess_text(user_input)
    if not cleaned_input.strip():
        return "Maaf, bisa tolong ketikkan pertanyaan yang lebih jelas?"

    # Transformasi input ke format TF-IDF
    user_vector = vectorizer.transform([cleaned_input])

    # Hitung Cosine Similarity antara input dengan semua pattern
    similarity = cosine_similarity(user_vector, tfidf_matrix)
    best_match_idx = similarity.argmax()
    score = similarity[0][best_match_idx]

    # Batas ambang kecocokan (Threshold)
    if score > 0.25:
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

# Baris penyesuaian port dinamis untuk lokal
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)