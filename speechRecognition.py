from flask import Flask, jsonify, request, render_template
import speech_recognition as sr
from gtts import gTTS
import os
import random
import csv
from flask import redirect, url_for
from flask import Response
from flask import session
from pathlib import Path

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
def index():
    return render_template('index.html', words=[], spoken_text=[])

@app.route('/listen', methods=['POST'])
def listen():
    # Get the number of seconds to listen from the request
    seconds = int(request.form['seconds'])

    # Call the listen_for function
    text = listen_for(seconds)

    # Return the recognized text as JSON
    # return jsonify({'text': text})
    return render_template('listenText.html', listen_text=text)

# computer will listen here
def listen_for(seconds: int):
    with sr.Microphone() as source:
        r = sr.Recognizer()
        print("Recognizing...")
        audio_data = r.record(source, seconds)
        text = r.recognize_google(audio_data)
        print(text)
        return text

# computer will speak alomst 10 words
# here spoken_words is a global variable now
@app.route('/speak', methods=['POST'])
def speak():
    # Initialize spoken_words as an empty list for each request
    spoken_words = []

    # Load the elementary vocabulary from CSV
    vocabulary = load_elementary_vocabulary()

    # Select and speak 10 random words
    for _ in range(10):
        random_word = random.choice(vocabulary)
        talk(random_word)
        spoken_words.append(random_word.lower())  # Convert to lowercase

    # Store spoken_words in the session
    session['spoken_words'] = spoken_words

    # Do not return anything, the function will complete without returning a response
    return Response(status=204)


# loading elementary_voc.csv
def load_elementary_vocabulary():
    vocabulary = []
    with open('/home/abhishek/Documents/TryingModel_Dyslexia/resources/elementary_voc.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            vocabulary.extend(row)
    return vocabulary

# talk will make speak google assistant speak
import time

def talk(text: str):
    # Initialize gTTS and specify language (here English)
    tts = gTTS(text=text, lang='en')

    # Save the speech as a temporary file
    tts.save("temp.mp3")

    # Play the speech using a media player for at least 4 seconds
    start_time = time.time()
    os.system("mpg321 temp.mp3")  # Adjust the command for your system if needed
    elapsed_time = time.time() - start_time

    # Wait for at least 4 seconds
    if elapsed_time < 4:
        time.sleep(4 - elapsed_time)

    # Remove the temporary file
    os.remove("temp.mp3")

# printing words taken by the user
@app.route('/submitWords', methods=['POST'])
def submit_words():
    # Get the submitted words from the form
    submitted_words = []
    for i in range(1, 11):
        word = request.form.get(f'word{i}', '')
        submitted_words.append(word)

    # Get spoken_words from the session
    spoken_words = session.get('spoken_words', [])

    # Render the template with the submitted words and spoken text
    return render_template('index.html', words=submitted_words, spoken_text=spoken_words)


if __name__ == '__main__':
    app.run(debug=True)
