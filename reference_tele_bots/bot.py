import os
import sys
sys.path.append('../../ChatterBot') # to use local copy of chatterbot
sys.path.append('../imageprocessing')

import time
import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import requests
import json
import random
import pickle
from PIL import Image, ImageEnhance
from PIL import ImageOps
from PIL import ImageFilter
from shutil import copyfile

# Boolean to check if message is sent
msg_sent = 0

#dictionary for users' states
chat_state_dict = {} #idle, upload_picture, is_uploading?,upload_pic_feedback, product_list_given

# List of tags and responses for product suggestion
couple_tags = ['couple','love']
family_tags = ['family','together','happiness']
celebration_tags = ['decoration','celebration']

#string resources
intro_reply = ["hi","hello","/start","hey"]
intro = "I am , a personalized chatbot from Cimpress. My existence rolls around helping you build a product, customize it, place an order, track it and to answer any of the tiny doubts you have.\n\n1. /enhance_pic - I'll guide you how to upload a 'good' picture and make enhancements to it, if necessary\n2. /typography - I'll use my expertise to suggest you the product on which the image will suit the best\n3.  /faq - I'll answer your questions as these problems are faced commonly\nApart, if you want to ask anything other than this, I'll always be there to help you out."

#initialise chatbot 
chatbot = ChatBot('Andrew', trainer = 'chatterbot.trainers.ChatterBotCorpusTrainer')
chatbot.train("chatterbot.corpus.english.faqs","chatterbot.corpus.english.conversations")
dontknow = "Sorry, I don't know how to respond. Would engage human(oid)s ;)"
# chatbotfaq = ChatBot('Symonds', trainer = 'chatterbot.trainers.ChatterBotCorpusTrainer')
# chatbotfaq
# chatbotfaq.train("chatterbot.corpus.english.faqs")

def imageTags(filepath):
	url = "http://api.imagga.com/v1/categorizations/nsfw_beta"

	api_key = 'acc_a8107ba13340888'
	api_secret = '2dc9a9e91dea0cd345b0aabd1bdac037'
	# image_url = 'http://www.rd.com/wp-content/uploads/sites/2/2016/04/01-cat-wants-to-tell-you-laptop.png'

	image_path = filepath

	response = requests.post('https://api.imagga.com/v1/content',
	auth=(api_key, api_secret),
	files={'image': open(image_path, 'r')})

	identifier = json.loads(response.content)["uploaded"][0]['id'];

	# print identifier

	response = requests.get('https://api.imagga.com/v1/tagging?url=%s', params={"content" : identifier},
						auth=(api_key, api_secret))

	listOfTagDicts = json.loads(response.content)["results"][0]["tags"]
	listOfTags = []

	for i in range (0,10):
		listOfTags.append(listOfTagDicts[i]["tag"])
	return listOfTags

def restrictedPic(filepath):
	print "Checking for inappropriate content"
	rl = "http://api.imagga.com/v1/categorizations/nsfw_beta"

	api_key = 'acc_a8107ba13340888'
	api_secret = '2dc9a9e91dea0cd345b0aabd1bdac037'
	# image_url = 'http://www.rd.com/wp-content/uploads/sites/2/2016/04/01-cat-wants-to-tell-you-laptop.png'

	image_path = filepath

	response = requests.post('https://api.imagga.com/v1/content',
	auth=(api_key, api_secret),
	files={'image': open(image_path, 'r')})

	identifier = json.loads(response.content)["uploaded"][0]['id'];

	# print identifier

	url = "http://api.imagga.com/v1/categorizations/nsfw_beta"

	# querystring = {"url":"http://playground.imagga.com/static/img/example_photo.png"}

	headers = {
		'accept': "application/json",
		'authorization': "Basic YWNjX2E4MTA3YmExMzM0MDg4ODoyZGM5YTllOTFkZWEwY2QzNDViMGFhYmQxYmRhYzAzNw=="
	}

	response = requests.request("GET", url, headers=headers, params={"content" : identifier})
	print json.loads(response.content)['results'][0]['categories'][0]['name']
	if(json.loads(response.content)['results'][0]['categories'][0]['name'] == 'nsfw'):
		return False
	else:
		return True
	# return json.loads(response.content)['results'][0]['categories'][0]['name']

def sendPic(path, user_id):
	url = "https://api.telegram.org/bot301610458:AAENDRBlt0BUulCFdoA0DqMxAt-shWYORfo/sendPhoto";
	files = {'photo': open(path, 'rb')}
	data = {'chat_id' : user_id}
	r= requests.post(url, files=files, data=data)

def ai_answer(question, chat_id) :
	global bot
	global chatbot
	answer = chatbot.get_response(question)
	if answer.confidence < 0.5 : 
		print "My confidence level is "+str(answer.confidence)
		bot.sendMessage(chat_id,dontknow)
		answer = dontknow + ". My human counterpart says: "
		true_answer = raw_input("Please answer :"+question + '\n')
		chatbot.set_trainer(ListTrainer)
		chatbot.train([question,true_answer])
		print "I have trained myself for it!!"
		return true_answer
	return str(answer)

def idle_action(msg,content_type, chat_type, chat_id):
	global bot
	global intro_reply
	global intro
	global chat_state_dict

	if content_type == 'text':
			msg_text = msg['text'].lower()

			if msg_text in intro_reply:
				init_greeting = "Hi " + msg['from']['first_name'] + ". How are you doing? But wait, let me introduce myself.\n\n"
				chat_state_dict[chat_id] = "idle"
				bot.sendMessage(chat_id,init_greeting + intro)
			elif msg_text == "/enhance_pic":
				upload_pic_msg_init = "Please upload a picture here"
				bot.sendMessage(chat_id,upload_pic_msg_init)
				chat_state_dict[chat_id] = "upload_picture"
			elif msg_text == "/typography":
				ask_text = "What text would you like to be stylised?"
				bot.sendMessage(chat_id,ask_text)
				chat_state_dict[chat_id] = "upload_text"
			elif msg_text == "/suggest_product":
				upload_pic_msg_init = "Please upload a picture here for which you want to know a suitable product"
				bot.sendMessage(chat_id,upload_pic_msg_init)
				chat_state_dict[chat_id] = "upload_product_picture"
			else:
				bot.sendMessage(chat_id,ai_answer(msg_text,chat_id))
				chat_state_dict[chat_id] = "idle"

def new_user(msg,content_type, chat_type, chat_id):
	#create a folder here
	user_id = msg['from']['id']
	if not os.path.exists("./" + str(user_id)):
		os.makedirs("./" + str(user_id))
	idle_action(msg,content_type, chat_type, chat_id)

def finalproduct(location):
	listofTags = imageTags(location)

	match_dict = {}
	match_dict["couple_match"] = 0
	match_dict["family_match"] = 0
	match_dict["celebration_match"] = 0

	for tag in listofTags:
		if tag in couple_tags:
			match_dict["couple_match"] += 1
		elif tag in family_tags:
			match_dict["family_match"] += 1
		elif tag in celebration_tags:
			match_dict["celebration_match"] += 1

	match_dict2 = sorted(match_dict, key=match_dict.__getitem__)
	match_category = match_dict2[-1]
	if(match_dict[match_category] == 0):
		# Default Case	
		defaultString = "I would probably suggest that you get this printed on a \n"
		print listofTags
		if("capital" in listofTags):
			return defaultString + "Mug"
		elif ("text" in listofTags):
			return defaultString + "Shirt"
		elif ("sign" in listofTags):
			return defaultString + "Shirt"
		elif ("protective covering" in listofTags):
			return defaultString + "Laptop Skins"
		else:
			return defaultString + "Laptop Skins"

	else:
		if(match_category == "couple_match"):
			# Couple
			return "I think you are trying to ink memories of your loved one " + "\xF0\x9F\x98\x8D" + " \n I would probably recommend a \n \t PILLOW"
		elif(match_category == "family_match"):
			# Family
			return "I think you are trying to capture your beautiful family " + "\xF0\x9F\x98\x8D" + " \n If you have more pics, maybe you can make a \n DESK CALENDAR"
		else:
			# Celebration
			return "Congratulations ! on the special occasion. I think you are  probably looking for a \n INVITATION CARD"

def textToImage(text, user_id):
	font_id = ['69296','8461','7445','6729','41072','30714','22892','4423','7299','31750','12057','11257','11159','11738','37448','10533']
	img_url = "http://www.ffonts.net/index.php?p=refresh&id="
	text = text.lower()
	random_font = random.sample(font_id,4)
	i = 1
	for font in random_font:
		complete_url = img_url + font + "&text=" + text
		r_img = requests.get(complete_url) 
		f = open(str(user_id)+'/typo'+str(i) + '.png','wb') 
		f.write(r_img.content) 
		f.close()
		i += 1

def colorenhancer(user_id, location):
	image = Image.open(location)
	contrast = ImageEnhance.Color(image)
	finalImage = contrast.enhance(1.5)
	finalImage.save(str(user_id)+'/enhanced.png')

def contrastenhancer(user_id, location):
	image = Image.open(location)
	finalImage = ImageOps.autocontrast(image,cutoff=5)
	finalImage.save(str(user_id)+'/enhanced.png')

def edgeenhancer(user_id, location):
	image = Image.open(location)
	finalImage = image.filter(ImageFilter.EDGE_ENHANCE)
	finalImage.save(str(user_id)+'/enhanced.png')


def enhance(user_id,filter):
	#to-do, save the image 'uploaded.png' as enhanced.png
	# os.rename(str(user_id)+'/uploaded.png',str(user_id)+'/enhanced.png')
	print filter
	if (filter == "color enhancer"):
		colorenhancer(user_id, str(user_id)+'/uploaded.png')
	elif (filter == "contrast enhancer"):
		contrastenhancer(user_id, str(user_id)+'/uploaded.png')
	elif (filter == "edge enhancer"):
		edgeenhancer(user_id, str(user_id)+'/uploaded.png')
	else:
		# os.rename(str(user_id)+'/uploaded.png',str(user_id)+'/enhanced.png')
		copyfile(str(user_id)+'/uploaded.png', str(user_id)+'/enhanced.png')
	pass

def select_typo(user_id, index):
	print "selecting typo function"
	copyfile(str(user_id)+'/typo'+str(index)+'.png',str(user_id)+'/enhanced.png')

def handle(msg):
	global bot
	content_type, chat_type, chat_id = telepot.glance(msg)
	user_id = msg['from']['id']
	# First check the state. If no state, then proceed towards general chat.
	if chat_id in chat_state_dict.keys():
		print chat_state_dict[chat_id]
		print "printed your state "
		if chat_state_dict[chat_id] == "idle":
			idle_action(msg,content_type,chat_type,chat_id)
		elif chat_state_dict[chat_id] == "upload_text":
			if content_type != 'text':
				chat_state_dict[chat_id] = "idle"
			else :
				textToImage(msg['text'],msg['from']['id'])
				for i in range(1,5):
					#to-do
					#file location is user_id/file+str(i)

					path = str(user_id) + "/typo" + str(i) + ".png"
					sendPic(path,msg['from']['id'])

					# bot.sendPhoto(chat_id,)
				pic_feedback = "Which typography do you like?"
				feedback_markup = ReplyKeyboardMarkup(keyboard=[['1', '2'],['3', '4'],],resize_keyboard=True)
				bot.sendMessage(chat_id,pic_feedback, reply_markup=feedback_markup)
				chat_state_dict[chat_id] = "typo_select"

		elif chat_state_dict[chat_id] == "typo_select":
			if content_type != 'text':
				chat_state_dict[chat_id] = "idle"
			else :
				# Suggest

				chat_state_dict[chat_id] = "idle"
				toast = "Selected the typography numbered " + msg['text']
				var = str(user_id)+"/"+"enhanced.png"
				final = finalproduct(var)

				remove_markup = ReplyKeyboardRemove()
				bot.sendMessage(chat_id,toast,reply_markup=remove_markup)
				bot.sendMessage(chat_id, str(final))
				select_typo(user_id,int(msg['text']))

		elif chat_state_dict[chat_id] == "upload_picture":
			if content_type != "photo":
				no_upload_msg = "I was expecting a picture" + u'\U0001f610' + "So is there some other issue? Do you still want to upload a picture?"
				still_upload_markup = ReplyKeyboardMarkup(keyboard=[['Yes', 'No'],],resize_keyboard=True)
				bot.sendMessage(chat_id,no_upload_msg, reply_markup=still_upload_markup)
				chat_state_dict[chat_id] = "is_uploading?"
			else:
				var = msg['from']['id']
				location = str(var) + '/uploaded' + '.png'
				bot.download_file(msg['photo'][-1]['file_id'], location)
				## Analyze the image and enhance it.
				if restrictedPic(location) == False :
					pic_analyzed_msg = "Inappropriate Content Detected. Try a more decent pic!! :D"
					bot.sendMessage(chat_id,pic_analyzed_msg)
					chat_state_dict[chat_id] = "idle"
				else:
					#give options for enhancing
					enhance_prompt = "Please select an option for enhancing your image"
					enhance_options = ReplyKeyboardMarkup(keyboard=[['Color Enhancer', 'Contrast Enhancer'],['Edge Enhancer', 'Original'],],resize_keyboard=True)
					bot.sendMessage(chat_id,enhance_prompt, reply_markup=enhance_options)
					chat_state_dict[chat_id] = "enhance"

		elif chat_state_dict[chat_id] == "enhance":
			if content_type == 'text':
				#save the enhanced images as enhanced
				option_selected = msg['text'].lower()
				if option_selected == "none":
					# Suggest
					var = str(user_id)+"/"+"enhanced.png"
					final = finalproduct(var)
					chat_state_dict[chat_id] = "idle"
					toast = "Originality retained! :)"
					remove_markup = ReplyKeyboardRemove()
					bot.sendMessage(chat_id,toast,reply_markup=remove_markup)
					bot.sendMessage(chat_id,toast)
					bot.sendMessage(chat_id, str(final))
				else:
					enhance(user_id,option_selected)
					pic_analyzed_msg = "I have enhanced the picture. Do have a look."
					remove_markup = ReplyKeyboardRemove()
					bot.sendMessage(chat_id,pic_analyzed_msg,reply_markup=remove_markup)
					# No pic to send. Sending same pic right now
					path = str(user_id) + "/enhanced.png"
					sendPic(path,user_id)
					pic_feedback = "Did you like the pictures?"
					feedback_markup = ReplyKeyboardMarkup(keyboard=[['Yes', 'No'],],resize_keyboard=True)
					bot.sendMessage(chat_id,pic_feedback, reply_markup=feedback_markup)
					chat_state_dict[chat_id] = "upload_pic_feedback"

		elif chat_state_dict[chat_id] == "is_uploading?":
			if content_type == 'text':
				if msg['text'].lower() == "yes":
					upload_pic_msg_init = "Please upload a picture here"
					remove_markup = ReplyKeyboardRemove()
					bot.sendMessage(chat_id,upload_pic_msg_init,reply_markup=remove_markup)
					chat_state_dict[chat_id] = "upload_picture"
				elif msg['text'].lower() == "no":
					back_to_base_msg = "Oh. What can I help you out with?"
					remove_markup = ReplyKeyboardRemove()
					bot.sendMessage(chat_id,back_to_base_msg,reply_markup=remove_markup)
					chat_state_dict[chat_id] = "idle"
				else:
					choose_yes_or_no = "Please choose between yes/no. Else, I'll be confused."
					bot.sendMessage(chat_id,choose_yes_or_no)


		elif chat_state_dict[chat_id] == "upload_pic_feedback":
			if content_type == 'text':
				if msg['text'].lower() == "yes":
					upload_pic_msg_init = "I am glad you liked it"
					remove_markup = ReplyKeyboardRemove()
					bot.sendMessage(chat_id,upload_pic_msg_init,reply_markup=remove_markup)
					# Suggest
					chat_state_dict[chat_id] = "idle"
					var = str(user_id)+"/"+"enhanced.png"
					final = finalproduct(var)
					toast = "Image successfully saved :)"
					bot.sendMessage(chat_id,toast)
					bot.sendMessage(chat_id, str(final))
				elif msg['text'].lower() == "no":
					back_to_base_msg = "Oh. Well, I'll try to improve next time"
					remove_markup = ReplyKeyboardRemove()
					bot.sendMessage(chat_id,back_to_base_msg,reply_markup=remove_markup)
					enhance_prompt = "Please select an option for enhancing your image"
					enhance_options = ReplyKeyboardMarkup(keyboard=[['Color Enhancer', 'Contrast Enhancer'],['Edge Enhancer', 'Original'],],resize_keyboard=True)
					bot.sendMessage(chat_id,enhance_prompt, reply_markup=enhance_options)
					chat_state_dict[chat_id] = "enhance"
				else:
					choose_yes_or_no = "Please choose between yes/no. Else, I'll be confused."
					bot.sendMessage(chat_id,choose_yes_or_no)


		elif chat_state_dict[chat_id] == "upload_product_picture":
			if content_type != "photo":
				no_upload_msg = "I was expecting a picture" + u'\U0001f610' + "So is there some other issue? Do you still want to upload a picture?"
				still_upload_markup = ReplyKeyboardMarkup(keyboard=[['Yes', 'No'],],resize_keyboard=True)
				bot.sendMessage(chat_id,no_upload_msg, reply_markup=still_upload_markup)

				chat_state_dict[chat_id] = "is_uploading?"
			else:
				location = str(var) + '/uploaded' + '.png'
				bot.download_file(msg['photo'][-1]['file_id'], location)

				## Analyze the image and suggest products
				## Maybe we can show templates if possible

				products_list_msg = "So here's what I feel. In order of appropriateness, the image can be used in a\n1. Pillow\n2. Mug\n3. T-shirt\n\n"                
				bot.sendMessage(chat_id,products_list_msg)
				msg_sent = 1
				chat_state_dict[chat_id] = "product_list_given"
		elif chat_state_dict[chat_id] == "picture_finalised":
			#to-do

			chat_state_dict[chat_id] = "idle";
			pass

	# No specific state. General questions then
	else:
		new_user(msg,content_type, chat_type, chat_id)


	# if content_type == "photo":
	#     # Get the photo file_id
	#     print msg['photo'][-1]['file_id']
	#     bot.download_file(msg['photo'][-1]['file_id'], './file.png')
	#     bot.sendPhoto(chat_id,msg['photo'][-1]['file_id'])

TOKEN = "301610458:AAENDRBlt0BUulCFdoA0DqMxAt-shWYORfo"  # get token from command-line

bot = telepot.Bot(TOKEN)
bot.message_loop(handle)
print ('Listening ...')

# Keep the program running.
while 1:
	time.sleep(1)