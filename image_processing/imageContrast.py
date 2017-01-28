from PIL import Image, ImageEnhance
from PIL import ImageOps
from PIL import ImageFilter

image = Image.open("./nsfw1.jpg")
# image.show()
finalImage = ImageOps.autocontrast(image,cutoff=5)
finalImage.save('enhanced.jpg')
