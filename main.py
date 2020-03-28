from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import os
import requests
import re

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['YOUR_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['YOUR_CHANNEL_SECRET'])

def reply(topic,len,event):
    reply_text = requests.post("https://api.howtobullshit.me/bullshit",json={"Topic":topic,"Minlen":len}).text
    reply_text = reply_text.replace("&nbsp;&nbsp;&nbsp;&nbsp;","　").replace("<br>","\n")

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text))

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    if re.match("^唬爛(哥)?\s([\d]+)(字)?\s(.*)",event.message.text):
        
        len = int(re.findall("^唬爛(哥)?\s([\d]+)(字)?\s(.*)",event.message.text)[0][1])
        topic = str(re.findall("^唬爛(哥)?\s([\d]+)(字)?\s(.*)",event.message.text)[0][3])
        #reply_text = "字數：{len},主題：{topic}".format(len=len,topic=topic)
        reply(topic,len,event)

    elif re.match("^唬爛(哥)?\s(.*)",event.message.text):

        len = 150
        topic = str(re.findall("^唬爛(哥)?\s(.*)",event.message.text)[0][1])
        reply(topic,len,event)

    elif re.match("^唬爛哥",event.message.text):
        
        len = 50
        topic = "唬爛"
        reply(topic,len,event)

if __name__ == "__main__":
    app.run()