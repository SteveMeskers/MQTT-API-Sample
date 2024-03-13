from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Union, Optional, List
from uuid import UUID
from datetime import datetime


class MqttBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel, from_attributes=True)

class ApiRequest(MqttBase):
    id: UUID
    data: Optional[dict] = None

class ApiResponse(MqttBase):
    data: Optional[dict] = None
    errors: Optional[dict] = None
    meta: Optional[dict] = None

class ApiEvent(MqttBase):
    data: dict

class AlarmSettingsData(MqttBase):
    volume: int = 100
    light_color: Union[str, None] = None
    sound: Union[str, None] = None
    trigger_alarm: bool = False
    light_enabled: bool = True
    ped_light_enabled: bool = True

class AlarmSettingsEnabled(MqttBase):
    enabled: bool

class AlarmEvent(MqttBase):
    epc: str = "123"
    timestamp: str = datetime.now().isoformat()
    reader: str = "Left Ped"

class StoreHours(MqttBase):
    day_of_week: str
    open_time: str
    close_time: str
    disable_light: bool
    disable_sound: bool

class StoreHoursGroup(MqttBase):
    store_hours: List[StoreHours]

class UpgradeMessage(MqttBase):
    update_fw: bool = False
    update_system_pkgs: bool = True
    time: Optional[str] = None

class AbReboot(MqttBase):
    time: Optional[str] = None

class ReaderReboot(MqttBase):
    reader_role: str
    time: Optional[str] = None

class AlarmHistoryEvent(MqttBase):
    epc: str = "123"
    timestamp: str = datetime.now().isoformat()
    reader: str = "Left Pedestal"
    tx: int = 1
    sold: bool = False
    audible: bool = True

class AlarmHistory(MqttBase):
    alarm_history: List[AlarmHistoryEvent]

class ReaderInfo(MqttBase):
    ip: str = "172.20.30.50"
    role: str = "Left Pedestal"
    fw_version: str = "123"
    online: bool = True
    serial_number: str = "333"

class ReadersInfo(MqttBase):
    readers: List[ReaderInfo] = [ReaderInfo()]

class SuppressionEvent(MqttBase):
    epc: str = "123"
    timestamp: str = datetime.now().isoformat()
    reader_role: Optional[str] = None
    som_suppressed: bool = True

class SuppressionHistory(MqttBase):
    supression_history: List[SuppressionEvent] = [SuppressionEvent()]
