#import mechanize

#br = mechanize.Browser()
#br.open("http://www.ffonts.net/?p=cat2&id=14&identify=&identifytext=&searchtext=&textinput=ritwick&nrresult=10&orderby=download&submit=Submit")


# br.form['ctl00$MainContent$txtname'] = 'Test Name'
# fill out other fields
import requests

img_url = "http://www.ffonts.net/index.php?p=refresh&id=69296&text=ritwick"

r_img = requests.get(img_url) 
f = open('000000.jpg','wb') 
f.write(r_img.content) 
f.close()
