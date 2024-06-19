import google.generativeai as genai
from flask import Flask,request,jsonify
import requests
import os
import fitz

wa_token=os.environ.get("WA_TOKEN")
genai.configure(api_key=os.environ.get("GEN_API"))
phone_id=os.environ.get("PHONE_ID")
#phone option is removed because now the bot can auto detect phone number
your_name="<Give your name, bot will consider this person as it's owner>"
bot_name="<Give name to your bot>"

pre_prompt=f'''I am using Gemini api for using you as a personal bot in WhatsApp, 
                   to assist me in various topics. So from now you are {bot_name} created by {your_name} (Yeah it's me and my name is {your_name}). 
                   And don't give any response to this prompt. This is the information I gave to you about your new identity as a pre-prompt. 
                   This message always gets executed when I run this bot script. 
                   So reply to only the prompts after this. Remember your new identity is {bot_name}.'''

app = Flask(__name__)
model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
convo = model.start_chat(history=[])
convo.send_message(pre_prompt)

def send(answer,sender):
    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    headers = {
        'Authorization': f'Bearer {wa_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "messaging_product": "whatsapp",
        "to": f"{sender}",
        "type": "text",
        "text": {"body": f"{answer}"},
    }
    response = requests.post(url, headers=headers, json=data)
    return response

def remove(*file_paths):
    for file in file_paths:
        if os.path.exists(file):
            os.remove(file)
        else:pass

@app.route("/", methods=["GET", "POST"])
def index():
    return "Bot"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == "BOT":
            return challenge, 200
        else:
            return "Failed", 403
    elif request.method == "POST":
        try:
            data = request.get_json()["entry"][0]["changes"][0]["value"]["messages"][0]
            sender="+"+data["from"]
            if data["type"] == "text":
                prompt = data["text"]["body"]
                convo.send_message(prompt)
                send(convo.last.text,sender)
            else:
                media_url_endpoint = f'https://graph.facebook.com/v18.0/{data[data["type"]]["id"]}/'
                headers = {'Authorization': f'Bearer {wa_token}'}
                media_response = requests.get(media_url_endpoint, headers=headers)
                media_url = media_response.json()["url"]
                media_download_response = requests.get(media_url, headers=headers)
                if data["type"] == "audio":
                    filename = "/tmp/temp_audio.mp3"
                elif data["type"] == "image":
                    filename = "/tmp/temp_image.jpg"
                elif data["type"] == "document":
                    doc=fitz.open(stream=media_download_response.content,filetype="pdf")
                    for _,page in enumerate(doc):
                        destination="/tmp/temp_image.jpg"
                        pix = page.get_pixmap()
                        pix.save(destination)
                        file = genai.upload_file(path=destination,display_name="tempfile")
                        response = model.generate_content(["What is this",file])
                        answer=response._result.candidates[0].content.parts[0].text
                        convo.send_message(f"user(me) can't send media files directly to you. So this message is created by an llm model based on the image prompt from user to you, reply to the user based on this: {answer}")
                        send(convo.last.text,sender)
                        remove(destination)
                else:send("This format is not Supported by the bot ☹",sender)
                with open(filename, "wb") as temp_media:
                    temp_media.write(media_download_response.content)
                file = genai.upload_file(path=filename,display_name="tempfile")
                response = model.generate_content(["What is this",file])
                answer=response._result.candidates[0].content.parts[0].text
                remove("/tmp/temp_image.jpg","/tmp/temp_audio.mp3")
                convo.send_message(f"I can't send media files directly to you. So this is an voice/image message to you from me(user) transcribed by an llm model, reply to me assuming you saw the media file: {answer}")
                send(convo.last.text,sender)
                files=genai.list_files()
                for file in files:
                    file.delete()
        except :pass
        return jsonify({"status": "ok"}), 200
if __name__ == "__main__":
    app.run(debug=True, port=8000)
