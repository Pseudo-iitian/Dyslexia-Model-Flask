from flask import Flask, jsonify, request, render_template
import speech_recognition as sr
from gtts import gTTS
import os
import random
import csv
import time
from flask import redirect, url_for
from flask import Response
from flask import session
from pathlib import Path
from textblob import TextBlob
# import streamlit as st
from PIL import Image
import os
import language_tool_python
import requests
import pandas as pd
import random
import speech_recognition as sr
import pyttsx3
import time
import eng_to_ipa as ipa
import requests
from abydos.phonetic import Soundex, Metaphone, Caverphone, NYSIIS


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


# image to text code starts here


# image to text ke liye
@app.route('/submit_text', methods=['POST'])
def submit_text():
  if request.method == 'POST':
    user_text = request.form['user_text']
    print("User submitted text:", user_text)

    # Use the user_text as input for get_feature_array
    feature_array = get_feature_array(user_text)
    result = score(feature_array)
    
    if result[0] == 1:
      word = "From the tests on this handwriting sample, there is a very slim chance that this person is suffering from dyslexia or dysgraphia"
      print("From the tests on this handwriting sample, there is a very slim chance that this person is suffering from dyslexia or dysgraphia")
    else:
      word = "From the tests on this handwriting sample, there is a very high chance that this person is suffering from dyslexia or dysgraphia"
      print("From the tests on this handwriting sample, there is a very high chance that this person is suffering from dyslexia or dysgraphia")

    # Render index.html and pass the prediction word
  return render_template('index.html', prediction=word)

def levenshtein(s1, s2):
  if len(s1) < len(s2):
    return levenshtein(s2, s1)

  # len(s1) >= len(s2)
  if len(s2) == 0:
    return len(s1)

  previous_row = range(len(s2) + 1)
  for i, c1 in enumerate(s1):
    current_row = [i + 1]
    for j, c2 in enumerate(s2):
    # j+1 instead of j since previous_row and current_row are one character longer
      insertions = previous_row[j + 1] + 1
      deletions = current_row[j] + 1       # than s2
      substitutions = previous_row[j] + (c1 != c2)
      current_row.append(min(insertions, deletions, substitutions))
    previous_row = current_row

  return previous_row[-1]

# ***************************************************

def spelling_accuracy(extracted_text):
  spell_corrected = TextBlob(extracted_text).correct()
  return ((len(extracted_text) - (levenshtein(extracted_text, spell_corrected)))/(len(extracted_text)+1))*100

# ***************************************************
my_tool = language_tool_python.LanguageTool('en-US')

def gramatical_accuracy(extracted_text):
  spell_corrected = TextBlob(extracted_text).correct()
  correct_text = my_tool.correct(spell_corrected)
  extracted_text_set = set(spell_corrected.split(" "))
  correct_text_set = set(correct_text.split(" "))
  n = max(len(extracted_text_set - correct_text_set),len(correct_text_set - extracted_text_set))
  return ((len(spell_corrected) - n)/(len(spell_corrected)+1))*100

# ****************************************************

# text correction API authentication
api_key_textcorrection = "eaeb9fb5a72f4e529111856dfabd43aa"
endpoint_textcorrection = "https://api.bing.microsoft.com/"

def percentage_of_corrections(extracted_text):
  data = {'text': extracted_text}
  params = {
    'mkt': 'en-us',
    'mode': 'proof'
  }
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Ocp-Apim-Subscription-Key': api_key_textcorrection,
  }
  response = requests.post(endpoint_textcorrection, headers=headers, params=params, data=data)
  json_response = response.json()
  flagged_tokens_count = len(json_response.get('flaggedTokens', []))
  extracted_word_count = len(extracted_text.split(" "))
  if extracted_word_count > 0:
    percentage_corrected = (flagged_tokens_count / extracted_word_count) * 100
  else:
    percentage_corrected = 0
  return percentage_corrected

# ****************************************************

def percentage_of_phonetic_accuraccy(extracted_text: str):
  soundex = Soundex()
  metaphone = Metaphone()
  caverphone = Caverphone()
  nysiis = NYSIIS()
  spell_corrected = TextBlob(extracted_text).correct()

  extracted_text_list = extracted_text.split(" ")
  extracted_phonetics_soundex = [soundex.encode(string) for string in extracted_text_list]
  extracted_phonetics_metaphone = [metaphone.encode(string) for string in extracted_text_list]
  extracted_phonetics_caverphone = [caverphone.encode(string) for string in extracted_text_list]
  extracted_phonetics_nysiis = [nysiis.encode(string) for string in extracted_text_list]

  extracted_soundex_string = " ".join(extracted_phonetics_soundex)
  extracted_metaphone_string = " ".join(extracted_phonetics_metaphone)
  extracted_caverphone_string = " ".join(extracted_phonetics_caverphone)
  extracted_nysiis_string = " ".join(extracted_phonetics_nysiis)

  spell_corrected_list = spell_corrected.split(" ")
  spell_corrected_phonetics_soundex = [soundex.encode(string) for string in spell_corrected_list]
  spell_corrected_phonetics_metaphone = [metaphone.encode(string) for string in spell_corrected_list]
  spell_corrected_phonetics_caverphone = [caverphone.encode(string) for string in spell_corrected_list]
  spell_corrected_phonetics_nysiis = [nysiis.encode(string) for string in spell_corrected_list]

  spell_corrected_soundex_string = " ".join(spell_corrected_phonetics_soundex)
  spell_corrected_metaphone_string = " ".join(spell_corrected_phonetics_metaphone)
  spell_corrected_caverphone_string = " ".join(spell_corrected_phonetics_caverphone)
  spell_corrected_nysiis_string = " ".join(spell_corrected_phonetics_nysiis)

  soundex_score = (len(extracted_soundex_string)-(levenshtein(extracted_soundex_string,spell_corrected_soundex_string)))/(len(extracted_soundex_string)+1)
  # print(spell_corrected_soundex_string)
  # print(extracted_soundex_string)
  # print(soundex_score)
  metaphone_score = (len(extracted_metaphone_string)-(levenshtein(extracted_metaphone_string,spell_corrected_metaphone_string)))/(len(extracted_metaphone_string)+1)
  # print(metaphone_score)
  caverphone_score = (len(extracted_caverphone_string)-(levenshtein(extracted_caverphone_string,spell_corrected_caverphone_string)))/(len(extracted_caverphone_string)+1)
  # print(caverphone_score)
  nysiis_score = (len(extracted_nysiis_string)-(levenshtein(extracted_nysiis_string,spell_corrected_nysiis_string)))/(len(extracted_nysiis_string)+1)
  # print(nysiis_score)
  return ((0.5*caverphone_score + 0.2*soundex_score + 0.2*metaphone_score + 0.1 * nysiis_score))*100

def calculate_score(extracted_phonetics, spell_corrected_phonetics):
    total_distance = sum(levenshtein(extracted, corrected) for extracted, corrected in zip(extracted_phonetics, spell_corrected_phonetics))
    return (1 - total_distance / len(extracted_phonetics)) if extracted_phonetics else 0

# def get_feature_array(path: str):
def get_feature_array(text):
  # path is the path of image, but i am using text.******************************IMAGE****************
  feature_array = []
  # extracted_text = image_to_text(path)
  # *****************************************************************************************
  extracted_text = text
  # *****************************************************************************************
  feature_array.append(spelling_accuracy(extracted_text))
  feature_array.append(gramatical_accuracy(extracted_text))
  feature_array.append(percentage_of_corrections(extracted_text))
  feature_array.append(percentage_of_phonetic_accuraccy(extracted_text))
  return feature_array

def generate_csv(folder: str, label: int, csv_name: str):
  arr = []
  for image in os.listdir(folder):
    path = os.path.join(folder, image)
    feature_array = get_feature_array(path)
    feature_array.append(label)
    # print(feature_array)
    arr.append(feature_array)
    print(feature_array)
  print(arr)
  pd.DataFrame(arr, columns=["spelling_accuracy", "gramatical_accuracy", " percentage_of_corrections",
                "percentage_of_phonetic_accuraccy", "presence_of_dyslexia"]).to_csv("test1.csv")

def score(input):
  if input[0] <= 96.40350723266602:
    var0 = [0.0, 1.0]
  else:
    if input[1] <= 99.1046028137207:
        var0 = [0.0, 1.0]
    else:
      if input[2] <= 2.408450722694397:
        if input[2] <= 1.7936508059501648:
            var0 = [1.0, 0.0]
        else:
            var0 = [0.0, 1.0]
      else:
            var0 = [1.0, 0.0]
  return var0

#image to text code completes here


if __name__ == '__main__':
    app.run(debug=True)
