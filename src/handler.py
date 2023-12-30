import random
import logging
import json
import os
import warnings

from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler,
    AbstractExceptionHandler,
    AbstractRequestInterceptor,
    AbstractResponseInterceptor,
)
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_model.interfaces.audioplayer import (
    PlayDirective,
    PlayBehavior,
    AudioItem,
    Stream,
    StopDirective,
    ClearQueueDirective,
    ClearBehavior,
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

warnings.filterwarnings("ignore", category=SyntaxWarning, module='ask_sdk_model')


# Audio stream metadata
STREAMS = [
    {
        "token": "1",
        "url": os.environ.get("RADIO_STREAM_URL","https://srv7021.dns-lcinternet.com/8060/stream"),
        "metadata": {
            "title": "Radio Samuel",
            "subtitle": "Radio Bahia Gibraltar",
            "art": {
                "sources": [
                    {
                        "contentDescription": "example image",
                        "url": "https://s3.amazonaws.com/cdn.dabblelab.com/img/audiostream-starter-512x512.png",
                        "widthPixels": 512,
                        "heightPixels": 512,
                    }
                ]
            },
            "backgroundImage": {
                "sources": [
                    {
                        "contentDescription": "example image",
                        "url": "https://s3.amazonaws.com/cdn.dabblelab.com/img/wayfarer-on-beach-1200x800.png",
                        "widthPixels": 1200,
                        "heightPixels": 800,
                    }
                ]
            },
        },
    }
]


class CheckAudioInterfaceHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        if handler_input.request_envelope.context.system.device:
            return (
                handler_input.request_envelope.context.system.device.supported_interfaces.audio_player
                is None
            )
        else:
            return False

    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = language_prompts["DEVICE_NOT_SUPPORTED"]

        return (
            handler_input.response_builder.speak(speech_output)
            .set_should_end_session(True)
            .response
        )


class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        stream = STREAMS[0]
        return (
            handler_input.response_builder.speak(
                "Starting {}".format(stream["metadata"]["title"])
            )
            .add_directive(
                PlayDirective(
                    play_behavior=PlayBehavior.REPLACE_ALL,
                    audio_item=AudioItem(
                        stream=Stream(
                            token=stream["token"],
                            url=stream["url"],
                            offset_in_milliseconds=0,
                            expected_previous_token=None,
                        ),
                        metadata=stream["metadata"],
                    ),
                )
            )
            .set_should_end_session(True)
            .response
        )


class ResumeStreamIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("PlaybackController.PlayCommandIssued")(
            handler_input
        ) or is_intent_name("AMAZON.ResumeIntent")(handler_input)

    def handle(self, handler_input):
        stream = STREAMS[0]
        return (
            handler_input.response_builder.add_directive(
                PlayDirective(
                    play_behavior=PlayBehavior.REPLACE_ALL,
                    audio_item=AudioItem(
                        stream=Stream(
                            token=stream["token"],
                            url=stream["url"],
                            offset_in_milliseconds=0,
                            expected_previous_token=None,
                        ),
                        metadata=stream["metadata"],
                    ),
                )
            )
            .set_should_end_session(True)
            .response
        )


class UnhandledFeaturesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (
            is_intent_name("AMAZON.LoopOnIntent")(handler_input)
            or is_intent_name("AMAZON.NextIntent")(handler_input)
            or is_intent_name("AMAZON.PreviousIntent")(handler_input)
            or is_intent_name("AMAZON.RepeatIntent")(handler_input)
            or is_intent_name("AMAZON.ShuffleOnIntent")(handler_input)
            or is_intent_name("AMAZON.StartOverIntent")(handler_input)
            or is_intent_name("AMAZON.ShuffleOffIntent")(handler_input)
            or is_intent_name("AMAZON.LoopOffIntent")(handler_input)
        )

    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["UNHANDLED"])
        return (
            handler_input.response_builder.speak(speech_output)
            .set_should_end_session(True)
            .response
        )


class AboutIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AboutIntent")(handler_input)

    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]

        speech_output = random.choice(language_prompts["ABOUT"])
        reprompt = random.choice(language_prompts["ABOUT_REPROMPT"])
        return (
            handler_input.response_builder.speak(speech_output).ask(reprompt).response
        )


class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["HELP"])
        reprompt = random.choice(language_prompts["HELP_REPROMPT"])

        return (
            handler_input.response_builder.speak(speech_output).ask(reprompt).response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (
            is_intent_name("AMAZON.CancelIntent")(handler_input)
            or is_intent_name("AMAZON.StopIntent")(handler_input)
            or is_intent_name("AMAZON.PauseIntent")(handler_input)
        )

    def handle(self, handler_input):
        return (
            handler_input.response_builder.add_directive(
                ClearQueueDirective(clear_behavior=ClearBehavior.CLEAR_ALL)
            )
            .add_directive(StopDirective())
            .set_should_end_session(True)
            .response
        )


class PlaybackStartedIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("AudioPlayer.PlaybackStarted")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.add_directive(
            ClearQueueDirective(clear_behavior=ClearBehavior.CLEAR_ENQUEUED)
        ).response


class PlaybackStoppedIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("PlaybackController.PauseCommandIssued")(
            handler_input
        ) or is_request_type("AudioPlayer.PlaybackStopped")(handler_input)

    def handle(self, handler_input):
        return (
            handler_input.response_builder.add_directive(
                ClearQueueDirective(clear_behavior=ClearBehavior.CLEAR_ALL)
            )
            .add_directive(StopDirective())
            .set_should_end_session(True)
            .response
        )


class PlaybackFailedIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("AudioPlayer.PlaybackFailed")(handler_input)

    def handle(self, handler_input):
        stream = STREAMS[0]
        return (
            handler_input.response_builder.add_directive(
                PlayDirective(
                    play_behavior=PlayBehavior.REPLACE_ALL,
                    audio_item=AudioItem(
                        stream=Stream(
                            token=stream["token"],
                            url=stream["url"],
                            offset_in_milliseconds=0,
                            expected_previous_token=None,
                        ),
                        metadata=stream["metadata"],
                    ),
                )
            )
            .set_should_end_session(True)
            .response
        )


# This handler handles utterances that can't be matched to any other intent handler.
class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["FALLBACK"])
        reprompt = random.choice(language_prompts["FALLBACK_REPROMPT"])

        return (
            handler_input.response_builder.speak(speech_output).ask(reprompt).response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        logger.info(
            "Session ended with reason: {}".format(
                handler_input.request_envelope.request.reason
            )
        )
        return handler_input.response_builder.response


class ExceptionEncounteredRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("System.ExceptionEncountered")(handler_input)

    def handle(self, handler_input):
        logger.info(
            "Session ended with reason: {}".format(
                handler_input.request_envelope.request.reason
            )
        )
        return handler_input.response_builder.response


class LocalizationInterceptor(AbstractRequestInterceptor):
    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        logger.info("Locale is {}".format(locale))
        locales_path = f"{os.path.dirname(__file__)}/languages/"
        try:
            with open(f"{locales_path}/{str(locale)}.json") as language_data:
                language_prompts = json.load(language_data)
        except:
            with open(f"{locales_path}/{str(locale[:2])}.json") as language_data:
                language_prompts = json.load(language_data)

        handler_input.attributes_manager.request_attributes["_"] = language_prompts


class RequestLogger(AbstractRequestInterceptor):
    def process(self, handler_input):
        logger.debug("Alexa Request: {}".format(handler_input.request_envelope.request))


class ResponseLogger(AbstractResponseInterceptor):
    def process(self, handler_input, response):
        logger.debug("Alexa Response: {}".format(response))


class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)

        language_prompts = handler_input.attributes_manager.request_attributes["_"]

        speech_output = language_prompts["ERROR"]
        reprompt = language_prompts["ERROR_REPROMPT"]

        return (
            handler_input.response_builder.speak(speech_output).ask(reprompt).response
        )


radio_skill = SkillBuilder()
radio_skill.add_request_handler(CheckAudioInterfaceHandler())
radio_skill.add_request_handler(LaunchRequestHandler())
radio_skill.add_request_handler(ResumeStreamIntentHandler())
radio_skill.add_request_handler(UnhandledFeaturesIntentHandler())
radio_skill.add_request_handler(CancelOrStopIntentHandler())
radio_skill.add_request_handler(HelpIntentHandler())
radio_skill.add_request_handler(AboutIntentHandler())
radio_skill.add_request_handler(FallbackIntentHandler())
radio_skill.add_request_handler(PlaybackStartedIntentHandler())
radio_skill.add_request_handler(PlaybackStoppedIntentHandler())
radio_skill.add_request_handler(PlaybackFailedIntentHandler())
radio_skill.add_request_handler(SessionEndedRequestHandler())
radio_skill.add_exception_handler(CatchAllExceptionHandler())
radio_skill.add_global_request_interceptor(LocalizationInterceptor())
radio_skill.add_global_request_interceptor(RequestLogger())
radio_skill.add_global_response_interceptor(ResponseLogger())

lambda_handler = radio_skill.lambda_handler()
