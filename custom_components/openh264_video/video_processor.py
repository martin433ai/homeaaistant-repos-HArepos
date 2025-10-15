"""
Video Processor Module for OpenH264 Integration.

This module provides the core video processing functionality including
H.264 encoding, decoding, and stream management for Home Assistant.
"""
from __future__ import annotations

import asyncio
import base64
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional, Tuple, List
from dataclasses import dataclass, field

from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta

from .const import (
    DEFAULT_TARGET_BITRATE,
    DEFAULT_MAX_FRAMERATE,
    DEFAULT_RESOLUTION,
    DEFAULT_PROFILE,
    DEFAULT_ENCODER_THREADS,
    FRAME_FORMAT_YUV420,
    FRAME_FORMAT_RGB24,
    RC_MODE_BITRATE,
    USAGE_TYPE_CAMERA,
    ERROR_INIT_FAILED,
    ERROR_ENCODING_FAILED,
    ERROR_DECODING_FAILED,
    ERROR_INVALID_PARAMETERS,
)
from .openh264_bindings import OpenH264Encoder, OpenH264Decoder, EUsageType, EVideoFormatType

_LOGGER = logging.getLogger(__name__)

@dataclass
class EncodingStats:
    """Statistics for encoding operations."""
    total_frames: int = 0
    successful_frames: int = 0
    failed_frames: int = 0
    total_encoding_time: float = 0.0
    total_bytes_encoded: int = 0
    average_bitrate: float = 0.0
    average_framerate: float = 0.0
    last_encoding_time: Optional[float] = None

@dataclass
class DecodingStats:
    """Statistics for decoding operations."""
    total_frames: int = 0
    successful_frames: int = 0
    failed_frames: int = 0
    total_decoding_time: float = 0.0
    total_bytes_decoded: int = 0
    last_decoding_time: Optional[float] = None

@dataclass
class StreamContext:
    """Context for an active stream."""
    stream_id: str
    encoder: Optional[OpenH264Encoder] = None
    decoder: Optional[OpenH264Decoder] = None
    width: int = 0
    height: int = 0
    bitrate: int = DEFAULT_TARGET_BITRATE
    framerate: float = DEFAULT_MAX_FRAMERATE
    format: str = FRAME_FORMAT_YUV420
    active: bool = True
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)

class VideoProcessor:
    """Main video processing class for OpenH264 operations."""
    
    def __init__(self, hass: HomeAssistant, config: Dict[str, Any]):
        """Initialize the video processor."""
        self.hass = hass
        self.config = config
        self._initialized = False
        
        # Threading
        self._executor = ThreadPoolExecutor(
            max_workers=config.get("encoder_threads", DEFAULT_ENCODER_THREADS),
            thread_name_prefix="openh264"
        )
        
        # Stream management
        self._active_streams: Dict[str, StreamContext] = {}
        self._stream_lock = asyncio.Lock()
        
        # Statistics
        self._encoding_stats = EncodingStats()
        self._decoding_stats = DecodingStats()
        self._stats_lock = asyncio.Lock()
        
        # Default encoder/decoder
        self._default_encoder: Optional[OpenH264Encoder] = None
        self._default_decoder: Optional[OpenH264Decoder] = None
        
        # Cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def async_initialize(self) -> None:
        """Initialize the video processor."""
        if self._initialized:
            return
        
        try:
            _LOGGER.info("Initializing video processor")
            
            # Create default encoder and decoder
            await self._create_default_codec_instances()
            
            # Start cleanup task for inactive streams
            self._cleanup_task = self.hass.async_create_task(
                self._cleanup_inactive_streams()
            )
            
            self._initialized = True
            _LOGGER.info("Video processor initialized successfully")
            
        except Exception as err:
            _LOGGER.error(f"Failed to initialize video processor: {err}")
            raise RuntimeError(ERROR_INIT_FAILED) from err
    
    async def _create_default_codec_instances(self) -> None:
        """Create default encoder and decoder instances."""
        loop = asyncio.get_event_loop()
        
        try:
            # Create encoder
            self._default_encoder = await loop.run_in_executor(
                self._executor, OpenH264Encoder
            )
            
            # Initialize encoder with default parameters
            width, height = self._parse_resolution(
                self.config.get("resolution", DEFAULT_RESOLUTION)
            )
            
            await loop.run_in_executor(
                self._executor,
                self._default_encoder.initialize,
                width,
                height,
                self.config.get("target_bitrate", DEFAULT_TARGET_BITRATE),
                self.config.get("max_framerate", DEFAULT_MAX_FRAMERATE),
                EUsageType.CAMERA_VIDEO_REAL_TIME
            )
            
            # Create decoder
            self._default_decoder = await loop.run_in_executor(
                self._executor, OpenH264Decoder
            )
            
            await loop.run_in_executor(
                self._executor, self._default_decoder.initialize
            )
            
            _LOGGER.debug("Default codec instances created")
            
        except Exception as err:
            _LOGGER.error(f"Failed to create default codec instances: {err}")
            raise
    
    async def encode_frame(
        self,
        frame_data: str,
        width: int,
        height: int,
        frame_format: str = FRAME_FORMAT_YUV420,
        quality: Optional[int] = None,
        stream_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Encode a single frame to H.264."""
        start_time = time.time()
        
        try:
            # Validate parameters
            if not frame_data or width <= 0 or height <= 0:
                raise ValueError(ERROR_INVALID_PARAMETERS)
            
            # Decode base64 frame data
            try:
                raw_frame_data = base64.b64decode(frame_data)
            except Exception as err:
                raise ValueError(f"Invalid base64 frame data: {err}")
            
            # Get or create encoder for this stream
            encoder = await self._get_encoder(stream_id, width, height)
            
            # Convert frame format if needed
            processed_frame = await self._convert_frame_format(
                raw_frame_data, frame_format, FRAME_FORMAT_YUV420, width, height
            )
            
            # Perform encoding in thread pool
            loop = asyncio.get_event_loop()
            encoded_data, result_code = await loop.run_in_executor(
                self._executor,
                encoder.encode_frame,
                processed_frame,
                width,
                height,
                int(time.time() * 1000)  # timestamp in milliseconds
            )
            
            # Update statistics
            encoding_time = time.time() - start_time
            async with self._stats_lock:
                self._encoding_stats.total_frames += 1
                self._encoding_stats.total_encoding_time += encoding_time
                self._encoding_stats.last_encoding_time = encoding_time
                
                if result_code == 0:
                    self._encoding_stats.successful_frames += 1
                    self._encoding_stats.total_bytes_encoded += len(encoded_data)
                else:
                    self._encoding_stats.failed_frames += 1
            
            # Encode result as base64
            encoded_b64 = base64.b64encode(encoded_data).decode('utf-8') if encoded_data else ""
            
            return {
                "success": result_code == 0,
                "encoded_data": encoded_b64,
                "encoding_time": encoding_time,
                "frame_size": len(encoded_data),
                "result_code": result_code,
                "width": width,
                "height": height,
                "format": frame_format
            }
            
        except Exception as err:
            async with self._stats_lock:
                self._encoding_stats.failed_frames += 1
            
            _LOGGER.error(f"Frame encoding failed: {err}")
            raise RuntimeError(ERROR_ENCODING_FAILED) from err
    
    async def decode_frame(
        self,
        bitstream_data: str,
        output_format: str = FRAME_FORMAT_YUV420,
        stream_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Decode H.264 bitstream to raw frame data."""
        start_time = time.time()
        
        try:
            # Validate parameters
            if not bitstream_data:
                raise ValueError(ERROR_INVALID_PARAMETERS)
            
            # Decode base64 bitstream data
            try:
                raw_bitstream = base64.b64decode(bitstream_data)
            except Exception as err:
                raise ValueError(f"Invalid base64 bitstream data: {err}")
            
            # Get decoder for this stream
            decoder = await self._get_decoder(stream_id)
            
            # Perform decoding in thread pool
            loop = asyncio.get_event_loop()
            decoded_data, width, height = await loop.run_in_executor(
                self._executor,
                decoder.decode_frame,
                raw_bitstream
            )
            
            # Convert frame format if needed
            if decoded_data and output_format != FRAME_FORMAT_YUV420:
                decoded_data = await self._convert_frame_format(
                    decoded_data, FRAME_FORMAT_YUV420, output_format, width, height
                )
            
            # Update statistics
            decoding_time = time.time() - start_time
            async with self._stats_lock:
                self._decoding_stats.total_frames += 1
                self._decoding_stats.total_decoding_time += decoding_time
                self._decoding_stats.last_decoding_time = decoding_time
                
                if decoded_data:
                    self._decoding_stats.successful_frames += 1
                    self._decoding_stats.total_bytes_decoded += len(decoded_data)
                else:
                    self._decoding_stats.failed_frames += 1
            
            # Encode result as base64
            decoded_b64 = base64.b64encode(decoded_data).decode('utf-8') if decoded_data else ""
            
            return {
                "success": bool(decoded_data),
                "decoded_data": decoded_b64,
                "decoding_time": decoding_time,
                "frame_size": len(decoded_data) if decoded_data else 0,
                "width": width,
                "height": height,
                "format": output_format
            }
            
        except Exception as err:
            async with self._stats_lock:
                self._decoding_stats.failed_frames += 1
            
            _LOGGER.error(f"Frame decoding failed: {err}")
            raise RuntimeError(ERROR_DECODING_FAILED) from err
    
    async def transcode_stream(
        self,
        input_stream: str,
        output_stream: str,
        target_bitrate: Optional[int] = None,
        target_resolution: Optional[str] = None
    ) -> None:
        """Transcode a video stream with different parameters."""
        _LOGGER.info(f"Starting stream transcoding: {input_stream} -> {output_stream}")
        
        # This is a placeholder implementation
        # In a real implementation, this would:
        # 1. Set up input stream reader
        # 2. Set up output stream writer
        # 3. Create encoder/decoder pair for transcoding
        # 4. Process frames in a loop
        # 5. Handle errors and cleanup
        
        await asyncio.sleep(0.1)  # Prevent blocking
        _LOGGER.warning("Stream transcoding is not yet fully implemented")
    
    async def adjust_entity_bitrate(self, entity_id: str, bitrate: int) -> None:
        """Adjust bitrate for a specific entity."""
        _LOGGER.info(f"Adjusting bitrate for {entity_id} to {bitrate}")
        
        # Find stream associated with entity
        async with self._stream_lock:
            for stream_context in self._active_streams.values():
                # This would need proper entity mapping
                if stream_context.active:
                    stream_context.bitrate = bitrate
                    # Reinitialize encoder with new bitrate if needed
                    break
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        async with self._stats_lock:
            # Calculate averages
            encoding_avg_time = (
                self._encoding_stats.total_encoding_time / max(1, self._encoding_stats.total_frames)
            )
            decoding_avg_time = (
                self._decoding_stats.total_decoding_time / max(1, self._decoding_stats.total_frames)
            )
            
            return {
                "encoding": {
                    "total_frames": self._encoding_stats.total_frames,
                    "successful_frames": self._encoding_stats.successful_frames,
                    "failed_frames": self._encoding_stats.failed_frames,
                    "success_rate": (
                        self._encoding_stats.successful_frames / max(1, self._encoding_stats.total_frames)
                    ),
                    "total_bytes": self._encoding_stats.total_bytes_encoded,
                    "average_time": encoding_avg_time,
                    "last_encoding_time": self._encoding_stats.last_encoding_time,
                },
                "decoding": {
                    "total_frames": self._decoding_stats.total_frames,
                    "successful_frames": self._decoding_stats.successful_frames,
                    "failed_frames": self._decoding_stats.failed_frames,
                    "success_rate": (
                        self._decoding_stats.successful_frames / max(1, self._decoding_stats.total_frames)
                    ),
                    "total_bytes": self._decoding_stats.total_bytes_decoded,
                    "average_time": decoding_avg_time,
                    "last_decoding_time": self._decoding_stats.last_decoding_time,
                },
                "active_streams": len(self._active_streams),
                "initialized": self._initialized,
            }
    
    async def _get_encoder(
        self, stream_id: Optional[str], width: int, height: int
    ) -> OpenH264Encoder:
        """Get encoder for stream, creating if necessary."""
        if not stream_id:
            return self._default_encoder
        
        async with self._stream_lock:
            if stream_id not in self._active_streams:
                # Create new stream context
                context = StreamContext(stream_id=stream_id, width=width, height=height)
                
                # Create encoder in thread pool
                loop = asyncio.get_event_loop()
                context.encoder = await loop.run_in_executor(
                    self._executor, OpenH264Encoder
                )
                
                # Initialize encoder
                await loop.run_in_executor(
                    self._executor,
                    context.encoder.initialize,
                    width,
                    height,
                    context.bitrate,
                    context.framerate,
                    EUsageType.CAMERA_VIDEO_REAL_TIME
                )
                
                self._active_streams[stream_id] = context
                _LOGGER.debug(f"Created encoder for stream {stream_id}")
            
            # Update activity timestamp
            self._active_streams[stream_id].last_activity = time.time()
            return self._active_streams[stream_id].encoder
    
    async def _get_decoder(self, stream_id: Optional[str]) -> OpenH264Decoder:
        """Get decoder for stream, creating if necessary."""
        if not stream_id:
            return self._default_decoder
        
        async with self._stream_lock:
            if stream_id not in self._active_streams:
                # Create new stream context
                context = StreamContext(stream_id=stream_id)
                
                # Create decoder in thread pool
                loop = asyncio.get_event_loop()
                context.decoder = await loop.run_in_executor(
                    self._executor, OpenH264Decoder
                )
                
                # Initialize decoder
                await loop.run_in_executor(
                    self._executor, context.decoder.initialize
                )
                
                self._active_streams[stream_id] = context
                _LOGGER.debug(f"Created decoder for stream {stream_id}")
            
            # Update activity timestamp
            self._active_streams[stream_id].last_activity = time.time()
            return self._active_streams[stream_id].decoder
    
    async def _convert_frame_format(
        self,
        frame_data: bytes,
        input_format: str,
        output_format: str,
        width: int,
        height: int
    ) -> bytes:
        """Convert frame between different formats."""
        if input_format == output_format:
            return frame_data
        
        # This is a placeholder for format conversion
        # In a real implementation, this would handle conversions between:
        # YUV420, RGB24, BGR24, RGBA, BGRA, etc.
        
        _LOGGER.debug(f"Converting frame from {input_format} to {output_format}")
        return frame_data  # No conversion for now
    
    async def _cleanup_inactive_streams(self) -> None:
        """Cleanup task to remove inactive streams."""
        while self._initialized:
            try:
                current_time = time.time()
                inactive_threshold = 300  # 5 minutes
                
                async with self._stream_lock:
                    inactive_streams = [
                        stream_id for stream_id, context in self._active_streams.items()
                        if current_time - context.last_activity > inactive_threshold
                    ]
                    
                    for stream_id in inactive_streams:
                        context = self._active_streams.pop(stream_id)
                        context.active = False
                        _LOGGER.debug(f"Cleaned up inactive stream: {stream_id}")
                
                # Sleep for 60 seconds before next cleanup
                await asyncio.sleep(60)
                
            except asyncio.CancelledError:
                break
            except Exception as err:
                _LOGGER.error(f"Error in cleanup task: {err}")
                await asyncio.sleep(60)
    
    @staticmethod
    def _parse_resolution(resolution: str) -> Tuple[int, int]:
        """Parse resolution string (e.g., '1920x1080') to width, height."""
        try:
            width, height = map(int, resolution.split('x'))
            return width, height
        except ValueError as err:
            raise ValueError(f"Invalid resolution format: {resolution}") from err
    
    async def async_cleanup(self) -> None:
        """Cleanup resources."""
        _LOGGER.info("Cleaning up video processor")
        
        self._initialized = False
        
        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Clean up active streams
        async with self._stream_lock:
            for context in self._active_streams.values():
                context.active = False
            self._active_streams.clear()
        
        # Shutdown thread pool
        if self._executor:
            self._executor.shutdown(wait=True)
        
        _LOGGER.info("Video processor cleanup completed")