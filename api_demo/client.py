import paho.mqtt.client as mqtt
from uuid import uuid4
from api_demo.topics import Topics
from api_demo.schemas import *

class Client:
    def __init__(self) -> None:
        self.mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt.on_connect = self.on_connect
        self.mqtt.connect("127.0.0.1", 1883)

    def on_connect(self, client: mqtt.Client, userdata, flags, rc, properties):
        client.subscribe(Topics.ALARM_EVENT)
        client.message_callback_add(Topics.ALARM_EVENT, self.handle_alarm_event)
        client.subscribe(Topics.SUPPRESSION_EVENT)
        client.message_callback_add(Topics.SUPPRESSION_EVENT, self.handle_suppression_event)

    def start(self):
        self.mqtt.loop_start()

    def stop(self):
        self.mqtt.loop_stop()

    def handle_alarm_event(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        api_model = ApiEvent.model_validate_json(message.payload)
        model = AlarmEvent.model_validate(api_model.data)
        print(f"Received alarm event: {model.model_dump_json()}")

    def handle_suppression_event(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        api_model = ApiEvent.model_validate_json(message.payload)
        model = SuppressionEvent.model_validate(api_model.data)
        print(f"Received supression event: {model.model_dump_json()}")

    def send_alarm_command(self):
        self._send_api_request(
            id=uuid4(),
            topic=Topics.COMMAND_ALARM,
            call_back=self.api_response,
            data=AlarmSettingsData().model_dump()
        )

    def api_response(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        self.mqtt.unsubscribe(message.topic)
        self.mqtt.message_callback_remove(message.topic)
        response = ApiResponse.model_validate_json(message.payload)

        if (door_id := response.meta.get("doorId", False)) and f"{door_id}/" not in message.topic:
            topic = "/".join([str(door_id), *message.topic.split("/")[:-1]])
            self._send_api_request(
                id=uuid4(),
                topic=topic,
                call_back=self.api_response
            )

        if response.errors:
            print(f"{message.topic}: Error happened: {response.errors}")
        else:
            print(f"{message.topic}: Successful")

    def config_default_alarm(self):
        self._send_api_request(
            id=uuid4(),
            topic=Topics.CONFIG_DEFAULT_ALARM,
            call_back=self.api_response,
            data=AlarmSettingsEnabled(enabled=False).model_dump(),
            retain=True
        )

    def config_store_hours(self):
        store_hours = StoreHours(
            day_of_week="Monday",
            open_time="11:11:11",
            close_time="12:12:12",
            disable_light=False,
            disable_sound=False
        )
        model = StoreHoursGroup(store_hours=[store_hours])
        self._send_api_request(
            id=uuid4(),
            topic=Topics.CONFIG_STORE_HOURS,
            call_back=self.api_response,
            data=model.model_dump(),
            retain=True
        )

    def config_alarm_settings(self):
        self._send_api_request(
            id=uuid4(),
            topic=Topics.CONFIG_ALARM_SETTING,
            call_back=self.api_response,
            data=AlarmSettingsData().model_dump(),
            retain=True
        )

    def send_upgrade_command(self):
        self._send_api_request(
            id=uuid4(),
            topic=Topics.COMMAND_UPGRADE,
            call_back=self.api_response,
            data=UpgradeMessage().model_dump(),
            retain=True
        )

    def send_ab_reboot_command(self):
        self._send_api_request(
            id=uuid4(),
            topic=Topics.COMMAND_REBOOT,
            call_back=self.api_response,
            data=AbReboot().model_dump(),
            retain=True
        )

    def send_reader_reboot_command(self):
        self._send_api_request(
            id=uuid4(),
            topic=Topics.COMMAND_READER_REBOOT,
            call_back=self.api_response,
            data=ReaderReboot(reader_role="Left Pedestal").model_dump(),
            retain=True
        )

    def send_alarm_history_request(self):
        self._send_api_request(
            id=uuid4(),
            topic=Topics.ALARM_HISTORY_INFO,
            call_back=self.api_response
        )

    def send_readers_info_request(self):
        self._send_api_request(
            id=uuid4(),
            topic=Topics.READERS_INFO,
            call_back=self.api_response
        )

    def send_suppression_history_request(self):
        self._send_api_request(
            id=uuid4(),
            topic=Topics.SUPPRESSION_HISTORY,
            call_back=self.api_response
        )

    def _send_api_request(self, id, topic, call_back, data=None, retain=False):
        print(f"Sending message to topic {topic} with id {id} and payload of {data}")
        request = ApiRequest(id=id, data=data).model_dump_json()
        response_topic = self.create_response_topic(topic, id)
        self.mqtt.subscribe(response_topic)
        self.mqtt.message_callback_add(response_topic, call_back)
        self.mqtt.publish(topic, request, retain=retain)

    def create_response_topic(self, topic, id):
        return f"{topic}/{id}"
