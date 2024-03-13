import paho.mqtt.client as mqtt
from api_demo.topics import Topics
from api_demo.schemas import *

class Driver:
    def __init__(self) -> None:
        self.mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_message = self.on_message
        self.mqtt.connect("127.0.0.1", 1883)
        self.door_id = 1
        self.store_id = 12
        self.account_id = 123
        self._topic_tracking = {}

    def on_connect(self, client: mqtt.Client, userdata, flags, rc, properties):
        for attr in dir(Topics):
            if not attr.startswith("__"):
                topic = Topics.__getattribute__(Topics, attr)

                if "event" not in topic:
                    client.subscribe(topic)
                    self._topic_tracking[topic] = False
                    door_topic = self._door_id_topic(topic)
                    client.subscribe(door_topic)
                    self._topic_tracking[door_topic] = False


    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        if self._check_topic_matches(message.topic, Topics.COMMAND_ALARM):
            self.handle_message(client, message, AlarmSettingsData)
        elif self._check_topic_matches(message.topic, Topics.COMMAND_UPGRADE):
            self.handle_message(client, message, UpgradeMessage)
        elif self._check_topic_matches(message.topic, Topics.CONFIG_DEFAULT_ALARM):
            self.handle_message(client, message, AlarmSettingsEnabled)
        elif self._check_topic_matches(message.topic, Topics.CONFIG_STORE_HOURS):
            self.handle_message(client, message, StoreHoursGroup)
        elif self._check_topic_matches(message.topic, Topics.CONFIG_ALARM_SETTING):
            self.handle_message(client, message, AlarmSettingsData)
        elif self._check_topic_matches(message.topic, Topics.COMMAND_REBOOT):
            self.handle_message(client, message, AbReboot)
        elif self._check_topic_matches(message.topic, Topics.COMMAND_READER_REBOOT):
            self.handle_message(client, message, ReaderReboot)
        elif self._check_topic_matches(message.topic, Topics.ALARM_HISTORY_INFO):
            self.handle_message(client, message, response_data=AlarmHistory(alarm_history = [AlarmEvent()]).model_dump())
        elif self._check_topic_matches(message.topic, Topics.READERS_INFO):
            self.handle_message(client, message, response_data=ReadersInfo().model_dump())
        elif self._check_topic_matches(message.topic, Topics.SUPPRESSION_HISTORY):
            self.handle_message(client, message, response_data=SuppressionHistory().model_dump())

    def _check_topic_matches(self, topic, expected_topic):
        door_topic = self._door_id_topic(expected_topic)

        if topic == expected_topic:
            self._topic_tracking[expected_topic] = True
            return True

        if topic == door_topic:
            self._topic_tracking[door_topic] = True
            return True

        return False

    def _door_id_topic(self, topic):
        return f"{self.door_id}/{topic}"

    def start(self):
        self.mqtt.loop_start()

    def stop(self):
        self.mqtt.loop_stop()

    def handle_message(self, client: mqtt.Client, message: mqtt.MQTTMessage, model_type: MqttBase = None, response_data: str = None):
        request = self.check_if_api_request(message.payload)

        if request:
            response_topic = self.create_response_topic(message.topic, request.id)
            try:
                if model_type:
                    model_type.model_validate(request.data)

                client.publish(response_topic, self._create_response(data=response_data))
            except Exception as e:
                client.publish(response_topic, self._create_response(errors={ "data": "Invalid payload" }))


    def check_if_api_request(self, data):
        try:
            return ApiRequest.model_validate_json(data)
        except ValueError:
            # Where to return with no ID
            print("No way to return")
            return None

    def create_response_topic(self, topic, id):
        return f"{topic}/{id}"

    def _create_response(self, data = None, errors = None) -> str:
        return ApiResponse(
            meta={
                "accountId": self.account_id,
                "doorId": self.door_id,
                "store_id": self.store_id
            },
            data=data,
            errors=errors
        ).model_dump_json()

    def alarm_event(self):
        print("Driver sending alarm event")
        self.mqtt.publish(Topics.ALARM_EVENT, ApiEvent(data=AlarmEvent().model_dump()).model_dump_json())

    def suppression_event(self):
        print("Driver sending suppression event")
        self.mqtt.publish(Topics.SUPPRESSION_EVENT, ApiEvent(data=SuppressionEvent().model_dump()).model_dump_json())

    def missing_topic_messages(self):
        return [topic for topic in self._topic_tracking if not self._topic_tracking[topic]]
