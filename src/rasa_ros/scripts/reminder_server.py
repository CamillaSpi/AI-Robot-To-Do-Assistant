#!/usr/bin/env python3
from rasa_ros.srv import Dialogue, DialogueResponse
from sanic import Sanic, response
from sanic.request import Request
from sanic.response import HTTPResponse
import rospy
import requests
from std_msgs.msg import String


pub = rospy.Publisher('toSpeech', String, queue_size=10)
pub2 = rospy.Publisher("toShow", String,  queue_size=10)

def create_app() -> Sanic:

    bot_app = Sanic("callback_server", configure_logging=False)

    @bot_app.post("/bot")
    def print_response(request: Request) -> HTTPResponse:
        """Print bot response to the console."""
        text = request.json.get("text")
        if text[0:2] == '-1':
            pub2.publish('http://10.0.1.248:80/webPage/')
            text = text[2:]
        elif text[0:2] == '-2':
            pub2.publish('http://10.0.1.248:80/webPage/')
            text = text[2:]
        pub.publish(text)

        body = {"status": "message sent"}
        return response.json(body, status=200)

    return bot_app

def handle_service(req):
    input_text = req.input_text
    id = req.id
    print('USER:' , input_text)
    # # Get answer        
    get_answer_url = 'http://localhost:5005/webhooks/callback/webhook'
    message = {
        "sender": id,
        "message": input_text
    }

    r = requests.post(get_answer_url, json=message)
    response = DialogueResponse()
    response.answer = str(r)

    return response


def main():
    rospy.init_node('callback')
    app = create_app()
    port = 5034
    s = rospy.Service('dialogue_server',
                        Dialogue, handle_service)
    rospy.logdebug('Dialogue server READY.')
    print(f"Starting callback server on port {port}.")
    app.run("0.0.0.0", port)
    rospy.spin()


if __name__ == '__main__':
    try: 
        main()
    except rospy.ROSInterruptException as e:
        pass
