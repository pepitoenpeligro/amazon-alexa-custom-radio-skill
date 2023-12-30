import json
import pytest
import os
from src.handler import lambda_handler


def read_event_lambda():
    event = {}
    with open(f"{os.path.dirname(__file__)}/event.data") as event_data:
        event = json.load(event_data)
    return event

def test_response_structure():
	event = read_event_lambda()
	context = {}
     
	sample_response = lambda_handler(event, context)
	assert 'version' in sample_response
	assert 'sessionAttributes' in sample_response
	assert 'userAgent' in sample_response
	assert 'response' in sample_response
	assert 'outputSpeech' in sample_response['response']
	assert 'directives' in sample_response['response']
	assert 'shouldEndSession' in sample_response['response']
     
def test_directives_structure():
    event = read_event_lambda()
    context = {}
    sample_response = lambda_handler(event, context)
    directives = sample_response['response']['directives']
    assert isinstance(directives, list)
    assert directives[0]['type'] == 'AudioPlayer.Play'
    
def test_stream_url():
    event = read_event_lambda()
    context = {}
    sample_response = lambda_handler(event, context)
    stream_url : str = sample_response['response']['directives'][0]['audioItem']['stream']['url']
    print(stream_url)
    assert  "https://" in stream_url
    

def test_stream_details():
    event = read_event_lambda()
    context = {}
    sample_response = lambda_handler(event, context)
    stream = sample_response['response']['directives'][0]['audioItem']['stream']
    assert stream['token'] == '1'
    assert stream['offsetInMilliseconds'] == 0
    
def test_session_end():
    event = read_event_lambda()
    context = {}
    sample_response = lambda_handler(event, context)
    assert sample_response['response']['shouldEndSession'] is True