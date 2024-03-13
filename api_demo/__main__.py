import time

from api_demo.driver import Driver
from api_demo.client import Client

if __name__ == '__main__':
    driver = Driver()
    client = Client()

    try:
        driver.start()
        client.start()
        time.sleep(1)

        client.send_alarm_command()
        client.config_default_alarm()
        driver.alarm_event()
        client.config_store_hours()
        client.config_alarm_settings()
        client.send_upgrade_command()
        client.send_ab_reboot_command()
        client.send_reader_reboot_command()
        client.send_alarm_history_request()
        client.send_readers_info_request()
        client.send_suppression_history_request()
        driver.suppression_event()

        time.sleep(10)
        print(f"Missing topic messages: {driver.missing_topic_messages()}")
    except Exception as e:
        print(e)
    finally:
        driver.stop()
        client.stop()

