import argparse
import sys
import urllib2
import xml.etree.ElementTree as ET
import re


def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "askWolfRam":
        return get_WolfRam(intent, session)
    elif intent_name == "AMAZON.NoIntent":
        return signoff()
    elif intent_name == "AMAZON.YesIntent":
        return get_help()
    elif intent_name == "AMAZON.HelpIntent":
        return get_help()
    elif intent_name == "AMAZON.CancelIntent":
        return get_help()
    elif intent_name == "AMAZON.StopIntent":
        return signoff()
    else:
        return get_help()


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
    session_attributes = {}
    card_title = "Welcome to Wolfram"
    speech_output = "Welcome to Wolf Ram Alpha, what is your question?"
    reprompt_text = "Can you repeat the question"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_WolfRam(intent, session):
    session_attributes = {}
    # To get appid, sign up at https://developer.wolframalpha.com/portal/apisignup.html
    app_id = "enter your app id"

    query = intent['slots']['response'].get('value')
    query = query.replace(' ', '%20')

    url = "http://api.wolframalpha.com/v2/query?podindex=2&format=plaintext&appid=" + app_id +"&input="+query
    data = urllib2.urlopen(url)
    dataxml = ET.parse(data)
    dataxmlroot = dataxml.getroot()

    result = "Wolfram Alpha doesn't understand your query. "

    if (dataxmlroot.get('success')):
        for plaintext in dataxmlroot.iter('plaintext'):
            result = plaintext.text

    query = query.replace('%20', ' ')
    speech_output = "The answer to your question: " + str(query) + " is: " + str(result) + " Would you like to ask another question?"
    reprompt_text = "I must be deaf, what did you say?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def get_help():
    session_attributes = {}
    card_title = "Help"
    speech_output = "Ask wolf ram alpha a question."
    should_end_session = False
    reprompt_text = "I must be deaf, what did you say?"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def signoff():
    session_attributes = {}
    card_title = "Signing off"
    speech_output = "This is wolf ram alpha signing off"
    should_end_session = True
    reprompt_text = ""
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def multiple_replace(dict, text):
    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
