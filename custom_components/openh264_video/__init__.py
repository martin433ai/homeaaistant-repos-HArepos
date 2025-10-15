"""
OpenH264 Video Processing Integration for Home Assistant.

This integration provides H.264 video encoding and decoding capabilities
using the OpenH264 library, specifically designed for security cameras
and video streaming applications.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    SERVICE_ENCODE_FRAME,
    SERVICE_DECODE_FRAME,
    SERVICE_TRANSCODE_STREAM,
    SERVICE_ADJUST_BITRATE,
    SERVICE_GET_STATS,
    EVENT_ENCODING_STARTED,
    EVENT_ENCODING_FINISHED,
    EVENT_DECODING_STARTED,
    EVENT_DECODING_FINISHED,
    EVENT_ERROR,
    CONF_TARGET_BITRATE,
    CONF_MAX_FRAMERATE,
    CONF_RESOLUTION,
    CONF_PROFILE,
    CONF_ENCODER_THREADS,
    DEFAULT_TARGET_BITRATE,
    DEFAULT_MAX_FRAMERATE,
    DEFAULT_RESOLUTION,
    DEFAULT_PROFILE,
    DEFAULT_ENCODER_THREADS,
    SUPPORTED_RESOLUTIONS,
    H264_PROFILES,
)
from .video_processor import VideoProcessor

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.CAMERA, Platform.SENSOR]

# Configuration schema
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_TARGET_BITRATE, default=DEFAULT_TARGET_BITRATE): cv.positive_int,
                vol.Optional(CONF_MAX_FRAMERATE, default=DEFAULT_MAX_FRAMERATE): vol.All(
                    vol.Coerce(float), vol.Range(min=1.0, max=60.0)
                ),
                vol.Optional(CONF_RESOLUTION, default=DEFAULT_RESOLUTION): vol.In(SUPPORTED_RESOLUTIONS),
                vol.Optional(CONF_PROFILE, default=DEFAULT_PROFILE): vol.In(H264_PROFILES),
                vol.Optional(CONF_ENCODER_THREADS, default=DEFAULT_ENCODER_THREADS): cv.positive_int,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

# Service schemas
SERVICE_ENCODE_FRAME_SCHEMA = vol.Schema({
    vol.Required("frame_data"): str,  # Base64 encoded frame data
    vol.Required("width"): cv.positive_int,
    vol.Required("height"): cv.positive_int,
    vol.Optional("format", default="yuv420"): str,
    vol.Optional("quality"): vol.All(vol.Coerce(int), vol.Range(min=1, max=51)),
})

SERVICE_DECODE_FRAME_SCHEMA = vol.Schema({
    vol.Required("bitstream_data"): str,  # Base64 encoded H.264 data
    vol.Optional("output_format", default="yuv420"): str,
})

SERVICE_TRANSCODE_STREAM_SCHEMA = vol.Schema({
    vol.Required("input_stream"): str,
    vol.Required("output_stream"): str,
    vol.Optional("target_bitrate"): cv.positive_int,
    vol.Optional("target_resolution"): vol.In(SUPPORTED_RESOLUTIONS),
})

SERVICE_ADJUST_BITRATE_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_ids,
    vol.Required("bitrate"): cv.positive_int,
})

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the OpenH264 video processing integration."""
    _LOGGER.info("Setting up OpenH264 video processing integration")
    
    # Store domain configuration
    hass.data.setdefault(DOMAIN, {})
    
    if DOMAIN in config:
        domain_config = config[DOMAIN]
        hass.data[DOMAIN]["config"] = domain_config
        _LOGGER.debug(f"Loaded configuration: {domain_config}")
    
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OpenH264 video processing from a config entry."""
    _LOGGER.info(f"Setting up OpenH264 entry: {entry.entry_id}")
    
    try:
        # Initialize the video processor
        processor = VideoProcessor(hass, entry.data)
        await processor.async_initialize()
        
        # Store the processor instance
        hass.data[DOMAIN][entry.entry_id] = processor
        
        # Set up platforms
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        
        # Register services
        await _async_register_services(hass, processor)
        
        _LOGGER.info(f"OpenH264 integration setup completed for entry {entry.entry_id}")
        return True
        
    except Exception as err:
        _LOGGER.error(f"Failed to set up OpenH264 integration: {err}")
        raise ConfigEntryNotReady from err

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info(f"Unloading OpenH264 entry: {entry.entry_id}")
    
    # Unload platforms
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Clean up the processor
        processor = hass.data[DOMAIN].pop(entry.entry_id, None)
        if processor:
            await processor.async_cleanup()
        
        # Unregister services if this is the last entry
        if not hass.data[DOMAIN]:
            _async_unregister_services(hass)
    
    return unload_ok

async def _async_register_services(hass: HomeAssistant, processor: VideoProcessor) -> None:
    """Register integration services."""
    _LOGGER.debug("Registering OpenH264 services")
    
    async def handle_encode_frame(call: ServiceCall) -> None:
        """Handle encode frame service call."""
        try:
            _LOGGER.debug("Handling encode_frame service call")
            hass.bus.async_fire(EVENT_ENCODING_STARTED, {"service_data": call.data})
            
            # Extract parameters
            frame_data = call.data["frame_data"]
            width = call.data["width"]
            height = call.data["height"]
            frame_format = call.data.get("format", "yuv420")
            quality = call.data.get("quality")
            
            # Perform encoding
            result = await processor.encode_frame(frame_data, width, height, frame_format, quality)
            
            # Fire completion event
            hass.bus.async_fire(EVENT_ENCODING_FINISHED, {
                "result": result,
                "service_data": call.data
            })
            
        except Exception as err:
            _LOGGER.error(f"Error in encode_frame service: {err}")
            hass.bus.async_fire(EVENT_ERROR, {
                "error": str(err),
                "service": SERVICE_ENCODE_FRAME,
                "service_data": call.data
            })
    
    async def handle_decode_frame(call: ServiceCall) -> None:
        """Handle decode frame service call."""
        try:
            _LOGGER.debug("Handling decode_frame service call")
            hass.bus.async_fire(EVENT_DECODING_STARTED, {"service_data": call.data})
            
            # Extract parameters
            bitstream_data = call.data["bitstream_data"]
            output_format = call.data.get("output_format", "yuv420")
            
            # Perform decoding
            result = await processor.decode_frame(bitstream_data, output_format)
            
            # Fire completion event
            hass.bus.async_fire(EVENT_DECODING_FINISHED, {
                "result": result,
                "service_data": call.data
            })
            
        except Exception as err:
            _LOGGER.error(f"Error in decode_frame service: {err}")
            hass.bus.async_fire(EVENT_ERROR, {
                "error": str(err),
                "service": SERVICE_DECODE_FRAME,
                "service_data": call.data
            })
    
    async def handle_transcode_stream(call: ServiceCall) -> None:
        """Handle transcode stream service call."""
        try:
            _LOGGER.debug("Handling transcode_stream service call")
            
            # Extract parameters
            input_stream = call.data["input_stream"]
            output_stream = call.data["output_stream"]
            target_bitrate = call.data.get("target_bitrate")
            target_resolution = call.data.get("target_resolution")
            
            # Perform transcoding
            await processor.transcode_stream(
                input_stream, output_stream, target_bitrate, target_resolution
            )
            
        except Exception as err:
            _LOGGER.error(f"Error in transcode_stream service: {err}")
            hass.bus.async_fire(EVENT_ERROR, {
                "error": str(err),
                "service": SERVICE_TRANSCODE_STREAM,
                "service_data": call.data
            })
    
    async def handle_adjust_bitrate(call: ServiceCall) -> None:
        """Handle adjust bitrate service call."""
        try:
            _LOGGER.debug("Handling adjust_bitrate service call")
            
            entity_ids = call.data["entity_id"]
            bitrate = call.data["bitrate"]
            
            # Adjust bitrate for specified entities
            for entity_id in entity_ids:
                await processor.adjust_entity_bitrate(entity_id, bitrate)
            
        except Exception as err:
            _LOGGER.error(f"Error in adjust_bitrate service: {err}")
            hass.bus.async_fire(EVENT_ERROR, {
                "error": str(err),
                "service": SERVICE_ADJUST_BITRATE,
                "service_data": call.data
            })
    
    async def handle_get_stats(call: ServiceCall) -> None:
        """Handle get stats service call."""
        try:
            _LOGGER.debug("Handling get_stats service call")
            
            stats = await processor.get_statistics()
            
            # Return stats via event
            hass.bus.async_fire(f"{DOMAIN}_stats", {"stats": stats})
            
        except Exception as err:
            _LOGGER.error(f"Error in get_stats service: {err}")
            hass.bus.async_fire(EVENT_ERROR, {
                "error": str(err),
                "service": SERVICE_GET_STATS
            })
    
    # Register services
    hass.services.async_register(
        DOMAIN, SERVICE_ENCODE_FRAME, handle_encode_frame, schema=SERVICE_ENCODE_FRAME_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_DECODE_FRAME, handle_decode_frame, schema=SERVICE_DECODE_FRAME_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_TRANSCODE_STREAM, handle_transcode_stream, schema=SERVICE_TRANSCODE_STREAM_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_ADJUST_BITRATE, handle_adjust_bitrate, schema=SERVICE_ADJUST_BITRATE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_GET_STATS, handle_get_stats
    )

def _async_unregister_services(hass: HomeAssistant) -> None:
    """Unregister integration services."""
    _LOGGER.debug("Unregistering OpenH264 services")
    
    services = [
        SERVICE_ENCODE_FRAME,
        SERVICE_DECODE_FRAME,
        SERVICE_TRANSCODE_STREAM,
        SERVICE_ADJUST_BITRATE,
        SERVICE_GET_STATS,
    ]
    
    for service in services:
        if hass.services.has_service(DOMAIN, service):
            hass.services.async_remove(DOMAIN, service)