#import mechanize

#br = mechanize.Browser()
#br.open("http://www.ffonts.net/?p=cat2&id=14&identify=&identifytext=&searchtext=&textinput=ritwick&nrresult=10&orderby=download&submit=Submit")


# br.form['ctl00$MainContent$txtname'] = 'Test Name'
# fill out other fields
import requests, random

font_id = ['69296','8461','7445','6729','41072','30714','22892','4423','7299','31750','12057','11257','11159','11738','37448','10533']
img_url = "http://www.ffonts.net/index.php?p=refresh&id="

def textToImage(text):

	text = text.lower()
	random_font = random.sample(font_id,4)
	i = 1

	for font in random_font:

		complete_url = img_url + font + "&text=" + text
		# print complete_url

		r_img = requests.get(complete_url) 
		f = open(str(i) + '.png','wb') 
		f.write(r_img.content) 
		f.close()

		i += 1

textToImage("ritwick")