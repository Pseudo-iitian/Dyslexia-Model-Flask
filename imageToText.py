import requests

api_url = 'https://api.api-ninjas.com/v1/imagetotext'
image_file_descriptor = open('/home/abhishek/Documents/TryingModel_Dyslexia/data/non_dyslexic/1.jpg', 'rb')
files = {'image': image_file_descriptor}
api_key = 'AQlZ6G6DYoLeBrESQdwLWQ==B0KFQzAOSV5DYAdB'  # Replace 'YOUR_API_KEY_HERE' with your actual API key
headers = {'X-Api-Key': api_key}
r = requests.post(api_url, files=files, headers=headers)

# Extracting text from the JSON response
response_json = r.json()
extracted_text = ""

for item in response_json:
    extracted_text += item['text'] + " "

print("Extracted Text:", extracted_text)
