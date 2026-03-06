"""Config flow for the HASL component."""
import voluptuous
import voluptuous as vol
import logging
import uuid
import httpx

from homeassistant import config_entries
from homeassistant.exceptions import HomeAssistantError
from homeassistant.core import callback

from .const import (
    DOMAIN,
    SCHEMA_VERSION,
    CONF_NAME,
    CONF_SITE_ID,
    SENSOR_RRARR,
    SENSOR_RRROUTE,
    SENSOR_RRDEP,
    SENSOR_STANDARD,
    SENSOR_STATUS,
    SENSOR_VEHICLE_LOCATION,
    SENSOR_DEVIATION,
    SENSOR_ROUTE,
    CONF_INTEGRATION_ID,
    CONF_INTEGRATION_TYPE,
    CONF_INTEGRATION_LIST,
)

CONF_SEARCH_STRING = 'search_string'
CONF_PICKED_LOCATION = 'picked_location'
SL_SITES_URL = 'https://transport.integration.sl.se/v1/sites'
SEARCH_AGAIN_OPTION = '↩ Search again'

from .config_schema import (
    hasl_base_config_schema,
    standard_config_option_schema,
    status_config_option_schema,
    vehiclelocation_config_option_schema,
    deviation_config_option_schema,
    route_config_option_schema,
    rrdep_config_option_schema,
    rrarr_config_option_schema,
    rrroute_config_option_schema
)

logger = logging.getLogger(f"custom_components.{DOMAIN}.config")


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for HASL."""

    VERSION = SCHEMA_VERSION
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    # FIXME: DOES NOT ACTUALLY VALIDATE ANYTHING! WE NEED THIS! =)
    async def validate_input(self, data):
        """Validate input in step user"""

        if not data[CONF_INTEGRATION_TYPE] in CONF_INTEGRATION_LIST:
            raise InvalidIntegrationType

        return data

    async def validate_config(self, data):
        """Validate input in step config"""

        return data

    async def async_step_user(self, user_input):
        """Handle the initial step."""
        logger.debug("[setup_integration] Entered")
        errors = {}

        if user_input is None:
            logger.debug("[async_step_user] No user input so showing creation form")
            return self.async_show_form(step_id="user", data_schema=voluptuous.Schema(hasl_base_config_schema(user_input, True)))

        try:
            user_input = await self.validate_input(user_input)
        except InvalidIntegrationType:
            errors["base"] = "invalid_integration_type"
            logger.debug("[setup_integration(validate)] Invalid integration type")
            return self.async_show_form(step_id="user", data_schema=voluptuous.Schema(hasl_base_config_schema(user_input, True)), errors=errors)
        except InvalidIntegrationName:
            errors["base"] = "invalid_integration_name"
            logger.debug("[setup_integration(validate)] Invalid integration type")
            return self.async_show_form(step_id="user", data_schema=voluptuous.Schema(hasl_base_config_schema(user_input, True)), errors=errors)
        except Exception:  # pylint: disable=broad-except
            errors["base"] = "unknown_exception"
            logger.debug("[setup_integration(validate)] Unknown exception occurred")
            return self.async_show_form(step_id="user", data_schema=voluptuous.Schema(hasl_base_config_schema(user_input, True)), errors=errors)

        id = str(uuid.uuid4())
        await self.async_set_unique_id(id)
        user_input[CONF_INTEGRATION_ID] = id
        self._userdata = user_input

        if user_input[CONF_INTEGRATION_TYPE] == SENSOR_STANDARD:
            return self.async_show_form(
                step_id="location_search",
                data_schema=voluptuous.Schema({vol.Required(CONF_SEARCH_STRING): str})
            )
        if user_input[CONF_INTEGRATION_TYPE] == SENSOR_STATUS:
            schema = status_config_option_schema()
        if user_input[CONF_INTEGRATION_TYPE] == SENSOR_VEHICLE_LOCATION:
            schema = vehiclelocation_config_option_schema()
        if user_input[CONF_INTEGRATION_TYPE] == SENSOR_DEVIATION:
            schema = deviation_config_option_schema()
        if user_input[CONF_INTEGRATION_TYPE] == SENSOR_ROUTE:
            schema = route_config_option_schema()
        if user_input[CONF_INTEGRATION_TYPE] == SENSOR_RRDEP:
            schema = rrdep_config_option_schema()
        if user_input[CONF_INTEGRATION_TYPE] == SENSOR_RRARR:
            schema = rrarr_config_option_schema()
        if user_input[CONF_INTEGRATION_TYPE] == SENSOR_RRROUTE:
            schema = rrroute_config_option_schema()

        return self.async_show_form(step_id="config", data_schema=voluptuous.Schema(schema), errors=errors)

    async def async_step_location_search(self, user_input):
        """Search for a stop by name using the SL transport API."""
        errors = {}
        search_schema = voluptuous.Schema({vol.Required(CONF_SEARCH_STRING): str})

        if user_input is None:
            return self.async_show_form(step_id="location_search", data_schema=search_schema)

        query = user_input[CONF_SEARCH_STRING].lower()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(SL_SITES_URL, timeout=10)
                all_sites = response.json()
        except Exception:
            errors["base"] = "location_search_failed"
            return self.async_show_form(step_id="location_search", data_schema=search_schema, errors=errors)

        sites = [s for s in all_sites if query in s.get('name', '').lower()]

        if not sites:
            errors[CONF_SEARCH_STRING] = "no_results"
            return self.async_show_form(step_id="location_search", data_schema=search_schema, errors=errors)

        # Store results as {display label: site_id}
        self._location_options = {
            f"{s['name']} (ID: {s['id']})": s['id'] for s in sites[:15]
        }
        options_list = [SEARCH_AGAIN_OPTION] + list(self._location_options.keys())

        return self.async_show_form(
            step_id="location_pick",
            data_schema=voluptuous.Schema({
                vol.Required(CONF_PICKED_LOCATION): vol.In(options_list)
            })
        )

    async def async_step_location_pick(self, user_input):
        """Handle stop selection from search results."""
        if user_input is None:
            return self.async_show_form(step_id="location_pick", data_schema=voluptuous.Schema({}))

        selected_label = user_input[CONF_PICKED_LOCATION]

        if selected_label == SEARCH_AGAIN_OPTION:
            return self.async_show_form(
                step_id="location_search",
                data_schema=voluptuous.Schema({vol.Required(CONF_SEARCH_STRING): str})
            )

        site_id = self._location_options[selected_label]
        self._userdata[CONF_SITE_ID] = site_id

        schema = standard_config_option_schema({CONF_SITE_ID: site_id})
        return self.async_show_form(step_id="config", data_schema=voluptuous.Schema(schema))

    async def async_step_config(self, user_input):
        """Handle a flow initialized by the user."""
        logger.debug("[setup_integration_config] Entered")
        errors = {}

        if self._userdata[CONF_INTEGRATION_TYPE] == SENSOR_STANDARD:
            schema = standard_config_option_schema(user_input)
        if self._userdata[CONF_INTEGRATION_TYPE] == SENSOR_STATUS:
            schema = status_config_option_schema(user_input)
        if self._userdata[CONF_INTEGRATION_TYPE] == SENSOR_VEHICLE_LOCATION:
            schema = vehiclelocation_config_option_schema(user_input)
        if self._userdata[CONF_INTEGRATION_TYPE] == SENSOR_DEVIATION:
            schema = deviation_config_option_schema(user_input)
        if self._userdata[CONF_INTEGRATION_TYPE] == SENSOR_ROUTE:
            schema = route_config_option_schema(user_input)
        if self._userdata[CONF_INTEGRATION_TYPE] == SENSOR_RRDEP:
            schema = rrdep_config_option_schema(user_input)         
        if self._userdata[CONF_INTEGRATION_TYPE] == SENSOR_RRARR:
            schema = rrarr_config_option_schema(user_input)         
        if self._userdata[CONF_INTEGRATION_TYPE] == SENSOR_RRROUTE:
            schema = rrroute_config_option_schema(user_input)         

        logger.debug(f"[setup_integration_config] Schema is {self._userdata[CONF_INTEGRATION_TYPE]}")

        # FIXME: DOES NOT ACTUALLY VALIDATE ANYTHING! WE NEED THIS! =)
        if user_input is not None:
            try:
                user_input = await self.validate_config(user_input)
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "unknown_exception"
                logger.debug("[setup_integration_config(validate)] Unknown exception occurred")
            else:
                try:
                    name = self._userdata[CONF_NAME]
                    del self._userdata[CONF_NAME]
                    logger.debug(f"[setup_integration_config] Creating entry '{name}' with id {self._userdata[CONF_INTEGRATION_ID]}")

                    self._userdata.update(user_input)

                    tempresult = self.async_create_entry(title=name, data=self._userdata)
                    logger.debug("[setup_integration_config] Entry creating succeeded")
                    return tempresult
                except:
                    logger.error(f"[setup_integration] Entry creation failed for '{name}' with id {self._userdata[CONF_INTEGRATION_ID]}")
                    return self.async_abort(reason="not_supported")

            logger.debug("[setup_integration_config] Validation errors encountered so showing options form again")
            return self.async_show_form(step_id="config", data_schema=voluptuous.Schema(schema), errors=errors)

        logger.debug("[setup_integration_config] No user input so showing options form")
        return self.async_show_form(step_id="config", data_schema=voluptuous.Schema(schema))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlow(config_entry)


class OptionsFlow(config_entries.OptionsFlow):
    """HASL config flow options handler."""

    def __init__(self, config_entry):
        """Initialize HASL options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return await self.async_step_user(user_input)

    async def validate_input(self, data):
        """Validate input in step user"""
        # FIXME: DOES NOT ACTUALLY VALIDATE ANYTHING! WE NEED THIS! =)

        return data

    async def async_step_user(self, user_input):
        """Handle a flow initialized by the user."""
        logger.debug("[integration_options] Entered")
        errors = {}

        if self.config_entry.data[CONF_INTEGRATION_TYPE] == SENSOR_STANDARD:
            schema = standard_config_option_schema(self.config_entry.data)
        if self.config_entry.data[CONF_INTEGRATION_TYPE] == SENSOR_STATUS:
            schema = status_config_option_schema(self.config_entry.data)
        if self.config_entry.data[CONF_INTEGRATION_TYPE] == SENSOR_VEHICLE_LOCATION:
            schema = vehiclelocation_config_option_schema(self.config_entry.data)
        if self.config_entry.data[CONF_INTEGRATION_TYPE] == SENSOR_DEVIATION:
            schema = deviation_config_option_schema(self.config_entry.data)
        if self.config_entry.data[CONF_INTEGRATION_TYPE] == SENSOR_ROUTE:
            schema = route_config_option_schema(self.config_entry.data)
        if self.config_entry.data[CONF_INTEGRATION_TYPE] == SENSOR_RRDEP:
            schema = rrdep_config_option_schema(self.config_entry.data)         
        if self.config_entry.data[CONF_INTEGRATION_TYPE] == SENSOR_RRARR:
            schema = rrarr_config_option_schema(self.config_entry.data)         
        if self.config_entry.data[CONF_INTEGRATION_TYPE] == SENSOR_RRROUTE:
            schema = rrroute_config_option_schema(self.config_entry.data)         

        logger.debug(f"[integration_options] Schema is {self.config_entry.data[CONF_INTEGRATION_TYPE]}")

        # FIXME: DOES NOT ACTUALLY VALIDATE ANYTHING! WE NEED THIS! =)
        if user_input is not None:
            try:
                user_input = await self.validate_input(user_input)
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "unknown_exception"
                logger.debug("[integration_options(validate)] Unknown exception occurred")
            else:
                try:
                    tempresult = self.async_create_entry(title=self.config_entry.title, data=user_input)
                    logger.debug("[integration_options] Entry update succeeded")
                    return tempresult
                except:
                    logger.error("[integration_options] Unknown exception occurred")

            logger.debug("[integration_options] Validation errors encountered so showing options form again")
            return self.async_show_form(step_id="user", data_schema=voluptuous.Schema(schema), errors=errors)

        logger.debug("[integration_options] No user input so showing options form")
        return self.async_show_form(step_id="user", data_schema=voluptuous.Schema(schema))


class InvalidIntegrationType(HomeAssistantError):
    """Error to indicate the integration is not of a valid type."""


class InvalidIntegrationName(HomeAssistantError):
    """Error to indicate that the name is not a legal name."""
