import sys
import telepot
from telepot.delegate import per_chat_id, create_open, pave_event_space

"""
$ python2.7 counter.py <token>
Counts number of messages a user has sent. Starts over if silent for 10 seconds.
Illustrates the basic usage of `DelegateBot` and `ChatHandler`.
"""

class MessageCounter(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MessageCounter, self).__init__(*args, **kwargs)
        self._count = 0

    def on_message(self, msg):
        self._count += 1
        self.sender.sendMessage(self._count)


TOKEN = "301610458:AAENDRBlt0BUulCFdoA0DqMxAt-shWYORfo"  # get token from command-line

bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, MessageCounter, timeout=10
    ),
])
bot.message_loop(run_forever='Listening ...')
