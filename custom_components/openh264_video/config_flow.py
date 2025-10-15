"""Config flow for OpenH264 Video Processing integration."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    CONF_TARGET_BITRATE,
    CONF_MAX_BITRATE,
    CONF_MIN_BITRATE,
    CONF_MAX_FRAMERATE,
    CONF_RESOLUTION,
    CONF_PROFILE,
    CONF_QUALITY_PRESET,
    CONF_ENCODER_THREADS,
    CONF_DECODER_THREADS,
    CONF_BUFFER_SIZE,
    DEFAULT_TARGET_BITRATE,
    DEFAULT_MAX_BITRATE,
    DEFAULT_MIN_BITRATE,
    DEFAULT_MAX_FRAMERATE,
    DEFAULT_RESOLUTION,
    DEFAULT_PROFILE,
    DEFAULT_QUALITY_PRESET,
    DEFAULT_ENCODER_THREADS,
    DEFAULT_DECODER_THREADS,
    DEFAULT_BUFFER_SIZE,
    SUPPORTED_RESOLUTIONS,
    H264_PROFILES,
    QUALITY_PRESETS,
)

_LOGGER = logging.getLogger(__name__)

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""

class OpenH264ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenH264 Video Processing."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return await self._show_setup_form()

        errors = {}

        try:
            # Validate the configuration
            await self._test_configuration(user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            # Configuration is valid, create the entry
            return self.async_create_entry(
                title=f"OpenH264 Video ({user_input[CONF_RESOLUTION]})",
                data=user_input,
            )

        return await self._show_setup_form(errors)

    async def _show_setup_form(self, errors: Optional[Dict] = None) -> FlowResult:
        """Show the setup form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_TARGET_BITRATE, default=DEFAULT_TARGET_BITRATE
                ): vol.All(vol.Coerce(int), vol.Range(min=100000, max=50000000)),
                vol.Optional(
                    CONF_MAX_FRAMERATE, default=DEFAULT_MAX_FRAMERATE
                ): vol.All(vol.Coerce(float), vol.Range(min=1.0, max=60.0)),
                vol.Optional(
                    CONF_RESOLUTION, default=DEFAULT_RESOLUTION
                ): vol.In(SUPPORTED_RESOLUTIONS),
                vol.Optional(
                    CONF_PROFILE, default=DEFAULT_PROFILE
                ): vol.In(H264_PROFILES),
                vol.Optional(
                    CONF_QUALITY_PRESET, default=DEFAULT_QUALITY_PRESET
                ): vol.In(QUALITY_PRESETS),
                vol.Optional(
                    CONF_ENCODER_THREADS, default=DEFAULT_ENCODER_THREADS
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=16)),
            }),
            errors=errors or {},
        )

    async def _test_configuration(self, config: Dict[str, Any]) -> None:
        """Test if the configuration is valid."""
        try:
            # Import here to avoid circular imports
            from .openh264_bindings import test_basic_functionality
            
            # Test if OpenH264 library can be loaded and basic functionality works
            if not test_basic_functionality():
                raise CannotConnect("OpenH264 library test failed")
                
            _LOGGER.info("OpenH264 configuration test passed")
            
        except Exception as err:
            _LOGGER.error(f"Configuration test failed: {err}")
            raise CannotConnect from err

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OpenH264OptionsFlow:
        """Create the options flow."""
        return OpenH264OptionsFlow(config_entry)

class OpenH264OptionsFlow(config_entries.OptionsFlow):
    """OpenH264 config flow options handler."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Get current options
        current_options = self.config_entry.options
        current_data = self.config_entry.data

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_TARGET_BITRATE,
                    default=current_options.get(
                        CONF_TARGET_BITRATE,
                        current_data.get(CONF_TARGET_BITRATE, DEFAULT_TARGET_BITRATE)
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=100000, max=50000000)),
                vol.Optional(
                    CONF_MAX_BITRATE,
                    default=current_options.get(CONF_MAX_BITRATE, DEFAULT_MAX_BITRATE),
                ): vol.All(vol.Coerce(int), vol.Range(min=100000, max=100000000)),
                vol.Optional(
                    CONF_MIN_BITRATE,
                    default=current_options.get(CONF_MIN_BITRATE, DEFAULT_MIN_BITRATE),
                ): vol.All(vol.Coerce(int), vol.Range(min=50000, max=10000000)),
                vol.Optional(
                    CONF_MAX_FRAMERATE,
                    default=current_options.get(
                        CONF_MAX_FRAMERATE,
                        current_data.get(CONF_MAX_FRAMERATE, DEFAULT_MAX_FRAMERATE)
                    ),
                ): vol.All(vol.Coerce(float), vol.Range(min=1.0, max=120.0)),
                vol.Optional(
                    CONF_QUALITY_PRESET,
                    default=current_options.get(
                        CONF_QUALITY_PRESET,
                        current_data.get(CONF_QUALITY_PRESET, DEFAULT_QUALITY_PRESET)
                    ),
                ): vol.In(QUALITY_PRESETS),
                vol.Optional(
                    CONF_ENCODER_THREADS,
                    default=current_options.get(
                        CONF_ENCODER_THREADS,
                        current_data.get(CONF_ENCODER_THREADS, DEFAULT_ENCODER_THREADS)
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=16)),
                vol.Optional(
                    CONF_DECODER_THREADS,
                    default=current_options.get(CONF_DECODER_THREADS, DEFAULT_DECODER_THREADS),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=16)),
                vol.Optional(
                    CONF_BUFFER_SIZE,
                    default=current_options.get(CONF_BUFFER_SIZE, DEFAULT_BUFFER_SIZE),
                ): vol.All(vol.Coerce(int), vol.Range(min=65536, max=16777216)),  # 64KB to 16MB
            }),
        )

    async def async_step_advanced(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle advanced options."""
        if user_input is not None:
            # Merge with existing options
            options = {**self.config_entry.options, **user_input}
            return self.async_create_entry(title="", data=options)

        current_options = self.config_entry.options

        return self.async_show_form(
            step_id="advanced",
            data_schema=vol.Schema({
                vol.Optional(
                    "enable_hardware_acceleration",
                    default=current_options.get("enable_hardware_acceleration", False),
                ): bool,
                vol.Optional(
                    "enable_multi_threading",
                    default=current_options.get("enable_multi_threading", True),
                ): bool,
                vol.Optional(
                    "enable_statistics",
                    default=current_options.get("enable_statistics", True),
                ): bool,
                vol.Optional(
                    "log_level",
                    default=current_options.get("log_level", "info"),
                ): vol.In(["debug", "info", "warning", "error"]),
                vol.Optional(
                    "stream_timeout",
                    default=current_options.get("stream_timeout", 300),
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=3600)),
            }),
        )

# Additional validation functions
def validate_bitrate_range(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate that bitrate values are in correct range."""
    min_bitrate = data.get(CONF_MIN_BITRATE, DEFAULT_MIN_BITRATE)
    target_bitrate = data.get(CONF_TARGET_BITRATE, DEFAULT_TARGET_BITRATE)
    max_bitrate = data.get(CONF_MAX_BITRATE, DEFAULT_MAX_BITRATE)

    if min_bitrate >= target_bitrate:
        raise vol.Invalid("Minimum bitrate must be less than target bitrate")
    
    if target_bitrate >= max_bitrate:
        raise vol.Invalid("Target bitrate must be less than maximum bitrate")

    return data

def validate_resolution_compatibility(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate resolution compatibility with target bitrate."""
    resolution = data.get(CONF_RESOLUTION, DEFAULT_RESOLUTION)
    target_bitrate = data.get(CONF_TARGET_BITRATE, DEFAULT_TARGET_BITRATE)
    
    # Parse resolution
    try:
        width, height = map(int, resolution.split('x'))
        pixels = width * height
        
        # Very rough bitrate recommendations based on resolution
        # These are conservative estimates for security cameras
        recommended_bitrates = {
            (640, 480): (200000, 1000000),      # 480p: 200kbps - 1Mbps
            (1280, 720): (500000, 3000000),     # 720p: 500kbps - 3Mbps  
            (1920, 1080): (1000000, 8000000),   # 1080p: 1Mbps - 8Mbps
            (3840, 2160): (5000000, 25000000),  # 4K: 5Mbps - 25Mbps
        }
        
        # Find closest resolution recommendation
        for (res_w, res_h), (min_rec, max_rec) in recommended_bitrates.items():
            if width <= res_w and height <= res_h:
                if target_bitrate < min_rec * 0.5:  # Allow 50% below minimum
                    _LOGGER.warning(
                        f"Target bitrate {target_bitrate} may be too low for {resolution}. "
                        f"Recommended: {min_rec}-{max_rec} bps"
                    )
                elif target_bitrate > max_rec * 2:  # Allow 100% above maximum
                    _LOGGER.warning(
                        f"Target bitrate {target_bitrate} may be too high for {resolution}. "
                        f"Recommended: {min_rec}-{max_rec} bps"
                    )
                break
                
    except ValueError:
        raise vol.Invalid(f"Invalid resolution format: {resolution}")

    return data