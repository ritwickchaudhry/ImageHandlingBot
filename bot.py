import sys
import time
import telepot

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    stickerID = "BQADAgADPwADyIsGAAGI1S2AmQ002AI"
    if content_type == 'text':
        bot.sendSticker(chat_id, stickerID)
    if content_type == "photo":
    	# Get the photo file_id
    	print msg['photo'][-1]['file_id']
    	bot.sendPhoto(chat_id,msg['photo'][-1]['file_id'])

TOKEN = "301610458:AAENDRBlt0BUulCFdoA0DqMxAt-shWYORfo"  # get token from command-line

bot = telepot.Bot(TOKEN)
bot.message_loop(handle)
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)