import os
import sys
import requests
import json

url = "http://api.imagga.com/v1/categorizations/nsfw_beta"

api_key = 'acc_a8107ba13340888'
api_secret = '2dc9a9e91dea0cd345b0aabd1bdac037'
# image_url = 'http://www.rd.com/wp-content/uploads/sites/2/2016/04/01-cat-wants-to-tell-you-laptop.jpg'

image_path = './file.png'

response = requests.post('https://api.imagga.com/v1/content',
auth=(api_key, api_secret),
files={'image': open(image_path, 'r')})

identifier = json.loads(response.content)["uploaded"][0]['id'];

# print identifier

url = "http://api.imagga.com/v1/categorizations/nsfw_beta"

# querystring = {"url":"http://playground.imagga.com/static/img/example_photo.jpg"}

headers = {
    'accept': "application/json",
    'authorization': "Basic YWNjX2E4MTA3YmExMzM0MDg4ODoyZGM5YTllOTFkZWEwY2QzNDViMGFhYmQxYmRhYzAzNw=="
}

response = requests.request("GET", url, headers=headers, params={"content" : identifier})

print json.loads(response.content)['results'][0]['categories'][0]['name']

# listOfTagDicts = json.loads(response.content)["results"][0]["tags"]
# listOfTags = []

# for i in range (0,5):
# 	listOfTags.append(listOfTagDicts[i]["tag"])
# print listOfTags
