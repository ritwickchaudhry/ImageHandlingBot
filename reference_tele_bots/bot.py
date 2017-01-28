import sys
import time
import telepot
sys.path.append('../../ChatterBot')
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from chatterbot import ChatBot
# Boolean to check if message is sent
msg_sent = 0

chat_state_dict = {}

intro_reply = ["hi","hello","/start","hey"]

intro = "I am , a personalized chatbot from Cimpress. My existence rolls around helping you build a product, customize it, place an order, track it and to answer any of the tiny doubts you have.\n\n1. /upload_pic - I'll guide you how to upload a 'good' picture and make enhancements to it, if necessary\n2. /suggest_product - I'll use my expertise to suggest you the product on which the image will suit the best\n3. /place_order - I'll guide you through the procedure to successfully place the order\n4. /track_order - I'll tell you the given delivery status of your ordered product and related information\n\nApart, if you want to ask anything other than this, I'll always be there to help you out."

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)
    msg_sent = 0

    # First check the state. If no state, then proceed towards general chat.
    if chat_id in chat_state_dict.keys():
        if chat_state_dict[chat_id] == "upload_picture":
            if content_type != "photo":
                no_upload_msg = "I was expecting a picture" + u'\U0001f610' + "So is there some other issue? Do you still want to upload a picture?"
                still_upload_markup = ReplyKeyboardMarkup(keyboard=[['Yes', 'No'],],resize_keyboard=True)
                bot.sendMessage(chat_id,no_upload_msg, reply_markup=still_upload_markup)
                msg_sent = 1
                chat_state_dict[chat_id] = "is_uploading?"
            else:
                bot.download_file(msg['photo'][-1]['file_id'], './file.jpg')
                
                ## Analyze the image and enhance it.
                
                pic_analyzed_msg = "I have enhanced the picture. Do have a look."
                bot.sendMessage(chat_id,pic_analyzed_msg)
                # No pic to send. Sending same pic right now
                bot.sendPhoto(chat_id,msg['photo'][-1]['file_id'])

                pic_feedback = "Did you like the pictures?"
                feedback_markup = ReplyKeyboardMarkup(keyboard=[['Yes', 'No'],],resize_keyboard=True)
                bot.sendMessage(chat_id,pic_feedback, reply_markup=feedback_markup)
                msg_sent = 1
                chat_state_dict[chat_id] = "upload_pic_feedback"

        elif chat_state_dict[chat_id] == "is_uploading?":
            if content_type == 'text':
                if msg['text'].lower() == "yes":
                    upload_pic_msg_init = "Please upload a picture here"
                    remove_markup = ReplyKeyboardRemove()
                    bot.sendMessage(chat_id,upload_pic_msg_init,reply_markup=remove_markup)
                    msg_sent = 1
                    chat_state_dict[chat_id] = "upload_picture"
                elif msg['text'].lower() == "no":
                    back_to_base_msg = "Oh. What can I help you out with?"
                    remove_markup = ReplyKeyboardRemove()
                    bot.sendMessage(chat_id,back_to_base_msg,reply_markup=remove_markup)
                    msg_sent = 1
                    chat_state_dict[chat_id] = "Idle"
                else:
                    choose_yes_or_no = "Please choose between yes/no. Else, I'll be confused."
                    bot.sendMessage(chat_id,choose_yes_or_no)
                    msg_sent = 1

        elif chat_state_dict[chat_id] == "upload_pic_feedback":
            if content_type == 'text':
                if msg['text'].lower() == "yes":
                    upload_pic_msg_init = "I am glad you liked it"
                    remove_markup = ReplyKeyboardRemove()
                    bot.sendMessage(chat_id,upload_pic_msg_init,reply_markup=remove_markup)
                    msg_sent = 1
                    chat_state_dict[chat_id] = "upload_pic_chosen"
                elif msg['text'].lower() == "no":
                    back_to_base_msg = "Oh. Well, I'll try to improve next time"
                    remove_markup = ReplyKeyboardRemove()
                    bot.sendMessage(chat_id,back_to_base_msg,reply_markup=remove_markup)
                    msg_sent = 1
                    chat_state_dict[chat_id] = "upload_pic_chosen"
                else:
                    choose_yes_or_no = "Please choose between yes/no. Else, I'll be confused."
                    bot.sendMessage(chat_id,choose_yes_or_no)
                    msg_sent = 1

        elif chat_state_dict[chat_id] == "upload_product_picture":
            if content_type != "photo":
                no_upload_msg = "I was expecting a picture" + u'\U0001f610' + "So is there some other issue? Do you still want to upload a picture?"
                still_upload_markup = ReplyKeyboardMarkup(keyboard=[['Yes', 'No'],],resize_keyboard=True)
                bot.sendMessage(chat_id,no_upload_msg, reply_markup=still_upload_markup)
                msg_sent = 1
                chat_state_dict[chat_id] = "is_uploading?"
            else:
                bot.download_file(msg['photo'][-1]['file_id'], './file.jpg')
                
                ## Analyze the image and suggest products
                ## Maybe we can show templates if possible

                products_list_msg = "So here's what I feel. In order of appropriateness, the image can be used in a\n1. Pillow\n2. Mug\n3. T-shirt\n\n"                
                bot.sendMessage(chat_id,products_list_msg)
                msg_sent = 1
                chat_state_dict[chat_id] = "product_list_given"
    chatbot = ChatBot(
	'Some Name',
	trainer = 'chatterbot.trainers.ChatterBotCorpusTrainer'	
    )
    # Train based on the english corpus
    chatbot.train("chatterbot.corpus.english.conversations")
    chatbot.train("chatterbot.corpus.english.humor")
    # No specific state. General questions then
    if msg_sent != 1:
        if content_type == 'text':
            msg_text = msg['text'].lower()

            if msg_text in intro_reply:
                init_greeting = "Hi " + msg['from']['first_name'] + ". How are you doing? But wait, let me introduce myself.\n\n"
                bot.sendMessage(chat_id,init_greeting + intro)
            elif msg_text == "/upload_pic":
                upload_pic_msg_init = "Please upload a picture here"
                bot.sendMessage(chat_id,upload_pic_msg_init)
                chat_state_dict[chat_id] = "upload_picture"
            elif msg_text == "/suggest_product":
                upload_pic_msg_init = "Please upload a picture here for which you want to know a suitable product"
                bot.sendMessage(chat_id,upload_pic_msg_init)
                chat_state_dict[chat_id] = "upload_product_picture"
            else:
                var = chatbot.get_response(msg_text)
                # print var
                bot.sendMessage(chat_id,str(var))

    # if content_type == "photo":
    # 	# Get the photo file_id
    # 	print msg['photo'][-1]['file_id']
    # 	bot.download_file(msg['photo'][-1]['file_id'], './file.jpg')
    # 	bot.sendPhoto(chat_id,msg['photo'][-1]['file_id'])

TOKEN = "301610458:AAENDRBlt0BUulCFdoA0DqMxAt-shWYORfo"  # get token from command-line

bot = telepot.Bot(TOKEN)
bot.message_loop(handle)
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)
