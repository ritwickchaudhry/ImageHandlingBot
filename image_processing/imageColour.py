from PIL import Image, ImageEnhance
from PIL import ImageOps
from PIL import ImageFilter

image = Image.open("./nsfw1.jpg")
# image.show()
contrast = ImageEnhance.Color(image)
finalImage = contrast.enhance(1.5)
finalImage.save('enhanced.jpg')
# ImageOps.autocontrast(image,cutoff=5).show()
