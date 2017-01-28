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

# Boolean to check if message is sent
msg_sent = 0

#dictionary for users' states
chat_state_dict = {} #idle, upload_picture, is_uploading?,upload_pic_feedback, product_list_given

#string resources
intro_reply = ["hi","hello","/start","hey"]
intro = "I am , a personalized chatbot from Cimpress. My existence rolls around helping you build a product, customize it, place an order, track it and to answer any of the tiny doubts you have.\n\n1. /upload_pic - I'll guide you how to upload a 'good' picture and make enhancements to it, if necessary\n2. /suggest_picture - I'll use my expertise to suggest you the product on which the image will suit the best\n3. /place_order - I'll guide you through the procedure to successfully place the order\n4. /track_order - I'll tell you the given delivery status of your ordered product and related information\n5. /faq - I'll answer your questions as these problems are faced commonly\nApart, if you want to ask anything other than this, I'll always be there to help you out."

#initialise chatbot 
chatbot = ChatBot('Andrew', trainer = 'chatterbot.trainers.ChatterBotCorpusTrainer')
chatbot.train("chatterbot.corpus.english.faqs")
dontknow = "Sorry, I don't know how to respond. Would engage human(oid)s ;)"
# chatbotfaq = ChatBot('Symonds', trainer = 'chatterbot.trainers.ChatterBotCorpusTrainer')
# chatbotfaq
# chatbotfaq.train("chatterbot.corpus.english.faqs")

class tele_user :
    def __init__(self, name):
        self.name = name

def imageTags(filepath):
    url = "http://api.imagga.com/v1/categorizations/nsfw_beta"

    api_key = 'acc_a8107ba13340888'
    api_secret = '2dc9a9e91dea0cd345b0aabd1bdac037'
    # image_url = 'http://www.rd.com/wp-content/uploads/sites/2/2016/04/01-cat-wants-to-tell-you-laptop.jpg'

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

    for i in range (0,5):
        listOfTags.append(listOfTagDicts[i]["tag"])
    return listOfTags

def restrictedPic(filepath):
    rl = "http://api.imagga.com/v1/categorizations/nsfw_beta"

    api_key = 'acc_a8107ba13340888'
    api_secret = '2dc9a9e91dea0cd345b0aabd1bdac037'
    # image_url = 'http://www.rd.com/wp-content/uploads/sites/2/2016/04/01-cat-wants-to-tell-you-laptop.jpg'

    image_path = './nsfw1.jpg'

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
    if(json.loads(response.content)['results'][0]['categories'][0]['name'] == 'nsfw'):
        return False
    else:
        return True
    # return json.loads(response.content)['results'][0]['categories'][0]['name']

def ai_answer(question) :
    global chatbot
    answer = chatbot.get_response(question)
    if answer.confidence < 0.5 : 
        print "My confidence level is "+str(answer.confidence)
        answer = dontknow
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
            elif msg_text == "/upload_pic":
                upload_pic_msg_init = "Please upload a picture here"
                bot.sendMessage(chat_id,upload_pic_msg_init)
                chat_state_dict[chat_id] = "upload_picture"
            elif msg_text == "/suggest_picture":
                ask_text = "What text would you like to be stylised?"
                bot.sendMessage(chat_id,ask_text)
                chat_state_dict[chat_id] = "upload_text"
            elif msg_text == "/suggest_product":
                upload_pic_msg_init = "Please upload a picture here for which you want to know a suitable product"
                bot.sendMessage(chat_id,upload_pic_msg_init)
                chat_state_dict[chat_id] = "upload_product_picture"
            else:
                bot.sendMessage(chat_id,ai_answer(msg_text))
                chat_state_dict[chat_id] = "idle"

def new_user(msg,content_type, chat_type, chat_id):
    #create a folder here
    user_id = msg['from']['id']
    if not os.path.exists("./" + str(user_id)):
        os.makedirs("./" + str(user_id))
    idle_action(msg,content_type, chat_type, chat_id)

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

def handle(msg):
    global bot
    content_type, chat_type, chat_id = telepot.glance(msg)
    user_id = msg['from']['id']
    # First check the state. If no state, then proceed towards general chat.
    if chat_id in chat_state_dict.keys():
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
                    url = "https://api.telegram.org/bot301610458:AAENDRBlt0BUulCFdoA0DqMxAt-shWYORfo/sendPhoto";
                    files = {'photo': open(path, 'rb')}
                    data = {'chat_id' : msg['from']['id']}
                    r= requests.post(url, files=files, data=data)
                    print r.json()

                    # bot.sendPhoto(chat_id,)
                pic_feedback = "Did you like the pictures?"
                feedback_markup = ReplyKeyboardMarkup(keyboard=[['Yes', 'No'],],resize_keyboard=True)
                bot.sendMessage(chat_id,pic_feedback, reply_markup=feedback_markup)
                chat_state_dict[chat_id] = "upload_pic_feedback"

        elif chat_state_dict[chat_id] == "upload_picture":
            if content_type != "photo":
                no_upload_msg = "I was expecting a picture" + u'\U0001f610' + "So is there some other issue? Do you still want to upload a picture?"
                still_upload_markup = ReplyKeyboardMarkup(keyboard=[['Yes', 'No'],],resize_keyboard=True)
                bot.sendMessage(chat_id,no_upload_msg, reply_markup=still_upload_markup)
                chat_state_dict[chat_id] = "is_uploading?"
            else:
                var = msg['from']['id']
                location = str(var) + '/uploaded' + '.jpg'
                bot.download_file(msg['photo'][-1]['file_id'], location)
                ## Analyze the image and enhance it.
                if(restrictedPic(location) == False):
                    pic_analyzed_msg = "Inappropriate Content Detected"
                    bot.sendMessage(chat_id,pic_analyzed_msg)
                    chat_state_dict[chat_id] = "idle"
                else:
                    pic_analyzed_msg = "I have enhanced the picture. Do have a look."
                    bot.sendMessage(chat_id,pic_analyzed_msg)
                    # No pic to send. Sending same pic right now
                    bot.sendPhoto(chat_id,msg['photo'][-1]['file_id'])
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
                    chat_state_dict[chat_id] = "idle"
                elif msg['text'].lower() == "no":
                    back_to_base_msg = "Oh. Well, I'll try to improve next time"
                    remove_markup = ReplyKeyboardRemove()
                    bot.sendMessage(chat_id,back_to_base_msg,reply_markup=remove_markup)
                    chat_state_dict[chat_id] = "idle"
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
                location = str(var) + '/uploaded' + '.jpg'
                bot.download_file(msg['photo'][-1]['file_id'], location)

                ## Analyze the image and suggest products
                ## Maybe we can show templates if possible

                products_list_msg = "So here's what I feel. In order of appropriateness, the image can be used in a\n1. Pillow\n2. Mug\n3. T-shirt\n\n"                
                bot.sendMessage(chat_id,products_list_msg)
                msg_sent = 1
                chat_state_dict[chat_id] = "product_list_given"

    # No specific state. General questions then
    else:
        new_user(msg,content_type, chat_type, chat_id)


    # if content_type == "photo":
    #     # Get the photo file_id
    #     print msg['photo'][-1]['file_id']
    #     bot.download_file(msg['photo'][-1]['file_id'], './file.jpg')
    #     bot.sendPhoto(chat_id,msg['photo'][-1]['file_id'])

TOKEN = "301610458:AAENDRBlt0BUulCFdoA0DqMxAt-shWYORfo"  # get token from command-line

bot = telepot.Bot(TOKEN)
bot.message_loop(handle)
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)