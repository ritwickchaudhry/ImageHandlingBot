import os
import sys
import requests
import json

url = "http://api.imagga.com/v1/categorizations/nsfw_beta"

api_key = 'acc_a8107ba13340888'
api_secret = '2dc9a9e91dea0cd345b0aabd1bdac037'
image_url = 'http://www.rd.com/wp-content/uploads/sites/2/2016/04/01-cat-wants-to-tell-you-laptop.jpg'

image_path = './file.png'

response = requests.post('https://api.imagga.com/v1/content',
auth=(api_key, api_secret),
files={'image': open(image_path, 'r')})

identifier = json.loads(response.content)["uploaded"][0]['id'];

print response.json()
print identifier

# response = requests.get('https://api.imagga.com/v1/croppings?url=%s', params={"content" : identifier},auth=(api_key, api_secret))


response = requests.get('https://api.imagga.com/v1/croppings?url=%s' % image_url,auth=(api_key, api_secret))


print response.json()
