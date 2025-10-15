"""Constants for the OpenH264 video component."""
from typing import Final

DOMAIN: Final = "openh264_video"

# Configuration keys
CONF_MAX_BITRATE: Final = "max_bitrate"
CONF_MIN_BITRATE: Final = "min_bitrate"
CONF_TARGET_BITRATE: Final = "target_bitrate"
CONF_MAX_FRAMERATE: Final = "max_framerate"
CONF_RESOLUTION: Final = "resolution"
CONF_PROFILE: Final = "profile"
CONF_QUALITY_PRESET: Final = "quality_preset"
CONF_ENCODER_THREADS: Final = "encoder_threads"
CONF_DECODER_THREADS: Final = "decoder_threads"
CONF_BUFFER_SIZE: Final = "buffer_size"

# Default values
DEFAULT_MAX_BITRATE: Final = 5000000  # 5 Mbps
DEFAULT_MIN_BITRATE: Final = 500000   # 500 Kbps
DEFAULT_TARGET_BITRATE: Final = 2000000  # 2 Mbps
DEFAULT_MAX_FRAMERATE: Final = 30.0
DEFAULT_RESOLUTION: Final = "1920x1080"
DEFAULT_PROFILE: Final = "baseline"
DEFAULT_QUALITY_PRESET: Final = "medium"
DEFAULT_ENCODER_THREADS: Final = 4
DEFAULT_DECODER_THREADS: Final = 4
DEFAULT_BUFFER_SIZE: Final = 1048576  # 1 MB

# Supported resolutions
SUPPORTED_RESOLUTIONS: Final = [
    "640x480",
    "800x600",
    "1024x768",
    "1280x720",
    "1920x1080",
    "2560x1440",
    "3840x2160"
]

# H.264 profiles
H264_PROFILES: Final = [
    "baseline",
    "main",
    "high"
]

# Quality presets
QUALITY_PRESETS: Final = [
    "ultrafast",
    "superfast", 
    "veryfast",
    "faster",
    "fast",
    "medium",
    "slow",
    "slower",
    "veryslow"
]

# Service names
SERVICE_ENCODE_FRAME: Final = "encode_frame"
SERVICE_DECODE_FRAME: Final = "decode_frame"
SERVICE_TRANSCODE_STREAM: Final = "transcode_stream"
SERVICE_ADJUST_BITRATE: Final = "adjust_bitrate"
SERVICE_GET_STATS: Final = "get_stats"

# Event types
EVENT_ENCODING_STARTED: Final = f"{DOMAIN}_encoding_started"
EVENT_ENCODING_FINISHED: Final = f"{DOMAIN}_encoding_finished"
EVENT_DECODING_STARTED: Final = f"{DOMAIN}_decoding_started"
EVENT_DECODING_FINISHED: Final = f"{DOMAIN}_decoding_finished"
EVENT_TRANSCODING_STARTED: Final = f"{DOMAIN}_transcoding_started"
EVENT_TRANSCODING_FINISHED: Final = f"{DOMAIN}_transcoding_finished"
EVENT_ERROR: Final = f"{DOMAIN}_error"

# Error codes
ERROR_INIT_FAILED: Final = "init_failed"
ERROR_ENCODING_FAILED: Final = "encoding_failed"
ERROR_DECODING_FAILED: Final = "decoding_failed"
ERROR_UNSUPPORTED_FORMAT: Final = "unsupported_format"
ERROR_INVALID_PARAMETERS: Final = "invalid_parameters"
ERROR_MEMORY_ERROR: Final = "memory_error"

# Frame formats
FRAME_FORMAT_YUV420: Final = "yuv420"
FRAME_FORMAT_RGB24: Final = "rgb24"
FRAME_FORMAT_BGR24: Final = "bgr24"
FRAME_FORMAT_RGBA: Final = "rgba"
FRAME_FORMAT_BGRA: Final = "bgra"

# Bitrate control modes
RC_MODE_QUALITY: Final = "quality"
RC_MODE_BITRATE: Final = "bitrate" 
RC_MODE_BUFFER: Final = "buffer"
RC_MODE_TIMESTAMP: Final = "timestamp"
RC_MODE_OFF: Final = "off"

# Usage types
USAGE_TYPE_CAMERA: Final = "camera_realtime"
USAGE_TYPE_SCREEN: Final = "screen_realtime"
USAGE_TYPE_CAMERA_NON_REALTIME: Final = "camera_non_realtime"

# Attribute names
ATTR_BITRATE: Final = "bitrate"
ATTR_FRAMERATE: Final = "framerate"
ATTR_RESOLUTION: Final = "resolution"
ATTR_PROFILE: Final = "profile"
ATTR_QUALITY: Final = "quality"
ATTR_ENCODED_FRAMES: Final = "encoded_frames"
ATTR_DECODED_FRAMES: Final = "decoded_frames"
ATTR_ENCODING_TIME: Final = "encoding_time"
ATTR_DECODING_TIME: Final = "decoding_time"
ATTR_FILE_SIZE: Final = "file_size"
ATTR_COMPRESSION_RATIO: Final = "compression_ratio"

# Sensor types
SENSOR_ENCODER_STATUS: Final = "encoder_status"
SENSOR_DECODER_STATUS: Final = "decoder_status"
SENSOR_ACTIVE_STREAMS: Final = "active_streams"
SENSOR_TOTAL_PROCESSED: Final = "total_processed"
SENSOR_ERROR_COUNT: Final = "error_count"

# Entity categories
ENTITY_CATEGORY_CONFIG: Final = "config"
ENTITY_CATEGORY_DIAGNOSTIC: Final = "diagnostic"