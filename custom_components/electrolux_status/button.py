"""Button platform for Electrolux Status."""

import logging

from pyelectroluxocp.oneAppApi import OneAppApi

from homeassistant.components.button import ENTITY_ID_FORMAT, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BUTTON, DOMAIN
from .entity import ElectroluxEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configure button platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    appliances = coordinator.data.get("appliances", None)
    if appliances is not None:
        for appliance_id, appliance in appliances.appliances.items():
            entities = [
                entity for entity in appliance.entities if entity.entity_type == BUTTON
            ]
            _LOGGER.debug(
                "Electrolux add %d BUTTON entities to registry for appliance %s",
                len(entities),
                appliance_id,
            )
            async_add_entities(entities)


class ElectroluxButtonEntity(ElectroluxEntity, ButtonEntity):
    """Electrolux Status button class."""

    def __init__(
        self,
        coordinator: any,
        name: str,
        config_entry,
        pnc_id: str,
        entity_type: str,
        entity_attr,
        entity_source,
        capability: dict[str, any],
        device_class: str,
        entity_category: EntityCategory,
        val_to_send,
        icon,
    ) -> None:
        """Initialize the Button Entity."""
        super().__init__(
            coordinator=coordinator,
            capability=capability,
            name=name,
            config_entry=config_entry,
            pnc_id=pnc_id,
            entity_type=entity_type,
            entity_attr=entity_attr,
            entity_source=entity_source,
            unit=None,
            device_class=device_class,
            entity_category=entity_category,
            icon=icon,
        )
        self.val_to_send = val_to_send
        self.button_icon = icon
        self.entity_id = ENTITY_ID_FORMAT.format(
            f"{self.get_appliance.brand}_{self.get_appliance.name}_{self.entity_source}_{self.entity_attr}_{self.val_to_send}"
        )

    @property
    def get_appliance(self):
        """Return the appliance object."""
        return self.coordinator.data["appliances"].get_appliance(self.pnc_id)

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""
        return f"{self.config_entry.entry_id}-{self.val_to_send}-{self.entity_attr}-{self.entity_source}-{self.pnc_id}"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "integration": DOMAIN,
        }

    @property
    def icon(self):
        """Return the icon of the button."""
        return self.button_icon

    @property
    def available(self):
        """Available state should depend on connect state."""
        return True

    async def send_command(self) -> bool:
        """Send a command to the device."""
        client: OneAppApi = self.api
        value = self.val_to_send
        if self.entity_source:
            command = {self.entity_source: {self.entity_attr: value}}
        else:
            command = {self.entity_attr: value}
        _LOGGER.debug("Electrolux send command %s", command)
        result = await client.execute_appliance_command(self.pnc_id, command)
        _LOGGER.debug("Electrolux send command result %s", result)
        return True

    async def async_press(self) -> None:
        """Execute a button press."""
        await self.send_command()
        # await self.hass.async_add_executor_job(self.send_command)
        # if self.entity_attr == "ExecuteCommand":
        #     await self.hass.async_add_executor_job(self.coordinator.api.setHacl, self.get_appliance.pnc_id, "0x0403", self.val_to_send, self.entity_source)
