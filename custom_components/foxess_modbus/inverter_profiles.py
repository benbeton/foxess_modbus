"""Defines the different inverter models and connection types"""
import logging
from typing import Any
from typing import Iterable

from homeassistant.config_entries import ConfigEntry

from .common.entity_controller import EntityController
from .const import INVERTER_BASE
from .const import INVERTER_CONN
from .entities import xx1_aux_binary_sensors
from .entities import xx1_aux_numbers
from .entities import xx1_aux_selects
from .entities import xx1_aux_sensors
from .entities import xx1_lan_sensors
from .entities.modbus_number import ModbusNumber
from .entities.modbus_number import ModbusNumberDescription
from .entities.modbus_select import ModbusSelect
from .entities.modbus_select import ModbusSelectDescription
from .entities.modbus_sensor import ModbusSensor
from .entities.modbus_sensor import SensorDescription
from .inverter_connection_types import CONNECTION_TYPES
from .inverter_connection_types import InverterConnectionType

_LOGGER = logging.getLogger(__package__)


class InverterModelConnectionTypeProfile:
    """Describes the capabilities of an inverter when connected to over a particular interface"""

    def __init__(
        self,
        connection_type: InverterConnectionType,
        sensors: list[SensorDescription],
        binary_sensors: list[SensorDescription],
        numbers: list[ModbusNumberDescription],
        selects: list[ModbusSelectDescription],
        address_ranges: list[tuple[int, int]],
    ) -> None:
        self.connection_type = connection_type
        self.sensors = sensors
        self.binary_sensors = binary_sensors
        self.numbers = numbers
        self.selects = selects

        self._address_ranges = address_ranges

    def create_read_ranges(self, max_read: int) -> Iterable[tuple[int, int]]:
        """
        Generates a set of read ranges to cover the addresses of all registers on this inverter,
        respecting the maxumum number of registers to read at a time

        :returns: Sequence of tuples of (start_address, num_registers_to_read)
        """

        # TODO: I want to make this a lot smarter. We know the addresses of all sensors, so we can use this to
        # generate an optimal sequence of reads
        for start, end in self._address_ranges:
            for i in range(start, end, max_read):
                data_per_read = min(max_read, end - i)
                yield (i, data_per_read)

    def create_sensors(
        self,
        controller: EntityController,
        entry: ConfigEntry,
        inverter_details: dict[str, Any],
    ) -> list[ModbusSensor]:
        """Instantiates all sensors for this connection type"""
        return list(
            ModbusSensor(controller, sensor, entry, inverter_details)
            for sensor in self.sensors
        )

    def create_binary_sensors(
        self,
        controller: EntityController,
        entry: ConfigEntry,
        inverter_details: dict[str, Any],
    ) -> list[ModbusSensor]:
        """Instantiates all binary sensors for this connection type"""
        return list(
            ModbusSensor(controller, sensor, entry, inverter_details)
            for sensor in self.binary_sensors
        )

    def create_numbers(
        self,
        controller: EntityController,
        entry: ConfigEntry,
        inverter_details: dict[str, Any],
    ) -> list[ModbusSensor]:
        """Instantiates all number entities for this connection type"""
        return list(
            ModbusNumber(controller, sensor, entry, inverter_details)
            for sensor in self.numbers
        )

    def create_selects(
        self,
        controller: EntityController,
        entry: ConfigEntry,
        inverter_details: dict[str, Any],
    ) -> list[ModbusSensor]:
        """Instantiates all number entities for this connection type"""
        return list(
            ModbusSelect(controller, sensor, entry, inverter_details)
            for sensor in self.selects
        )


class InverterModelProfile:
    """Describes the capabilities of an inverter model"""

    def __init__(
        self, model: str, connection_types: list[InverterModelConnectionTypeProfile]
    ) -> None:
        self.model = model
        self.connection_types = {x.connection_type.key: x for x in connection_types}


INVERTER_PROFILES = {
    x.model: x
    for x in [
        InverterModelProfile(
            model="H1",
            connection_types=[
                InverterModelConnectionTypeProfile(
                    connection_type=CONNECTION_TYPES["AUX"],
                    sensors=xx1_aux_sensors.H1_SENSORS + xx1_aux_sensors.H1_AC1_SENSORS,
                    binary_sensors=xx1_aux_binary_sensors.SENSORS,
                    numbers=xx1_aux_numbers.NUMBERS,
                    selects=xx1_aux_selects.SELECTS,
                    address_ranges=[
                        (11000, 11050),
                        (41000, 41012),
                    ],
                ),
                InverterModelConnectionTypeProfile(
                    connection_type=CONNECTION_TYPES["LAN"],
                    sensors=xx1_lan_sensors.H1_SENSORS + xx1_lan_sensors.H1_AC1_SENSORS,
                    binary_sensors=[],
                    numbers=[],
                    selects=[],
                    address_ranges=[(31000, 31025)],
                ),
            ],
        ),
        InverterModelProfile(
            model="AC1",
            connection_types=[
                InverterModelConnectionTypeProfile(
                    connection_type=CONNECTION_TYPES["AUX"],
                    sensors=xx1_aux_sensors.H1_AC1_SENSORS,
                    binary_sensors=xx1_aux_binary_sensors.SENSORS,
                    numbers=xx1_aux_numbers.NUMBERS,
                    selects=xx1_aux_selects.SELECTS,
                    address_ranges=[
                        (11000, 11050),
                        (41000, 41012),
                    ],
                ),
                InverterModelConnectionTypeProfile(
                    connection_type=CONNECTION_TYPES["LAN"],
                    sensors=xx1_lan_sensors.H1_AC1_SENSORS,
                    binary_sensors=[],
                    numbers=[],
                    selects=[],
                    address_ranges=[(31000, 31025)],
                ),
            ],
        ),
        InverterModelProfile(
            model="AIO-H1",
            connection_types=[
                InverterModelConnectionTypeProfile(
                    connection_type=CONNECTION_TYPES["AUX"],
                    sensors=xx1_aux_sensors.H1_SENSORS + xx1_aux_sensors.H1_AC1_SENSORS,
                    binary_sensors=xx1_aux_binary_sensors.SENSORS,
                    numbers=xx1_aux_numbers.NUMBERS,
                    selects=xx1_aux_selects.SELECTS,
                    address_ranges=[
                        (11000, 11050),
                        (41000, 41012),
                    ],
                ),
                InverterModelConnectionTypeProfile(
                    connection_type=CONNECTION_TYPES["LAN"],
                    sensors=xx1_lan_sensors.H1_SENSORS + xx1_lan_sensors.H1_AC1_SENSORS,
                    binary_sensors=[],
                    numbers=[],
                    selects=[],
                    address_ranges=[(31000, 31025)],
                ),
            ],
        ),
    ]
}


def inverter_connection_type_profile_from_config(
    inverter_config: dict[str, Any]
) -> InverterModelConnectionTypeProfile:
    """Fetches a InverterConnectionTypeProfile for a given configuration object"""

    return INVERTER_PROFILES[inverter_config[INVERTER_BASE]].connection_types[
        inverter_config[INVERTER_CONN]
    ]
