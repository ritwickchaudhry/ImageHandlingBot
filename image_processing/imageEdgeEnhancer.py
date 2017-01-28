from PIL import Image, ImageEnhance
from PIL import ImageOps
from PIL import ImageFilter

image = Image.open("./nsfw1.jpg")
# image.show()
finalImage = image.filter(ImageFilter.EDGE_ENHANCE)
finalImage.save('enhanced.jpg')
# ImageOps.autocontrast(image,cutoff=5).show()
