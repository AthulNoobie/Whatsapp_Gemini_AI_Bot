import google.generativeai as genai
from flask import Flask,request,jsonify
import requests

token="Your Whatsapp API key"
genai.configure(api_key="Your Gemini API key")
app=Flask(__name__)

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 8192,
}

safety_settings = [
  {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  { "category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_MEDIUM_AND_ABOVE"},  
  {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

convo = model.start_chat(history=[
])

convo.send_message('''I am using Gemini api for using you as a personal bot in whatsapp,
				   for respond to messages in my absence. 
				   So from now you are "Heck Bot" craeted by Athul ( Yeah it's me and my full name is Athul A S). 
				   And don't give any response to this prompt. 
				   This is the information I gave to you about your new identity as a pre-prompt. 
				   This message always gets executed when i run this bot script. 
				   So reply to only the prompts after this. Remeber your new identity is Heck Bot.''')

def send(answer):
    url="https://graph.facebook.com/v18.0/Your Phone number id/messages"
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data={
          "messaging_product": "whatsapp", 
          "to": "Your Phone number with country code", 
          "type": "text",
          "text":{"body": f"{answer}"},
          }
    
    response=requests.post(url, headers=headers,json=data)
    return response

@app.route("/",methods=["GET","POST"])
def index():
    return "Bot"

@app.route("/webhook",methods=["GET","POST"])
def webhook():
    if request.method=="GET":
        mode=request.args.get("hub.mode")
        token=request.args.get("hub.verify_token")
        challenge=request.args.get("hub.challenge")
        if mode=="subscribe" and token == "BOT":
            return challenge,200
        else:return "Failed",403
    elif request.method=="POST":
        try:
            prompt=request.get_json()["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
            convo.send_message(prompt)
            send(convo.last.text)
        except KeyError:pass
        return jsonify({"status": "ok"}), 200
if __name__=="__main__":
    app.run(debug=True, port=8000)
