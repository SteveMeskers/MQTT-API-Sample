from dataclasses import dataclass

@dataclass
class Topics:
    CONFIG_DEFAULT_ALARM = "sfero/config/alarms/default"
    CONFIG_STORE_HOURS = "sfero/config/store/hours"
    CONFIG_ALARM_SETTING = "sfero/config/alarms/settings"

    COMMAND_ALARM = "sfero/command/alarm"
    COMMAND_UPGRADE = "sfero/command/upgrade"
    COMMAND_REBOOT = "sfero/command/reboot"
    COMMAND_READER_REBOOT = "sfero/command/readers/reboot"

    ALARM_EVENT = "sfero/event/alarms"
    SUPPRESSION_EVENT = "sfero/event/suppression/tags"

    READERS_INFO = "sfero/info/readers"
    ALARM_HISTORY_INFO = "sfero/info/alarms/history"
    SUPPRESSION_HISTORY = "sfero/info/suppression/history"
