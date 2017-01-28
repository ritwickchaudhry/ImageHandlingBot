import os
import sys
import requests

url = "https://api.cimpress.io/sandbox/vcs/printapi/v2/documents/creators/file"
image_path = "./nsfw1.jpg"
response = requests.post(url, params={"sku" : "VIP-45403", "file" : open(image_path, 'r')})

print response
