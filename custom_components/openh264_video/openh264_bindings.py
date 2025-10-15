"""
OpenH264 Python Bindings using ctypes

This module provides Python wrappers for the OpenH264 C API,
enabling H.264 encoding and decoding functionality in Python.
"""
import ctypes
import os
import platform
from ctypes import (
    CDLL, POINTER, Structure, Union, c_int, c_uint, c_void_p,
    c_char_p, c_float, c_bool, c_long, c_ubyte, c_uint8, c_uint16,
    c_uint32, c_int32, c_int64, byref, cast
)
from typing import Optional, Tuple, List
import logging

_LOGGER = logging.getLogger(__name__)

# Platform-specific library loading
def _load_openh264_library() -> CDLL:
    """Load the OpenH264 library based on the current platform."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    if platform.system() == "Darwin":  # macOS
        lib_path = os.path.join(current_dir, "libopenh264.2.6.0.dylib")
    elif platform.system() == "Windows":
        lib_path = os.path.join(current_dir, "openh264.dll")
    else:  # Linux and others
        lib_path = os.path.join(current_dir, "libopenh264.so")
    
    if not os.path.exists(lib_path):
        raise FileNotFoundError(f"OpenH264 library not found at {lib_path}")
    
    try:
        return CDLL(lib_path)
    except OSError as e:
        raise OSError(f"Failed to load OpenH264 library: {e}")

# Load the library
try:
    _lib = _load_openh264_library()
    _LOGGER.info("OpenH264 library loaded successfully")
except Exception as e:
    _LOGGER.error(f"Failed to load OpenH264 library: {e}")
    raise

# Constants from codec_app_def.h
MAX_TEMPORAL_LAYER_NUM = 4
MAX_SPATIAL_LAYER_NUM = 4
MAX_QUALITY_LAYER_NUM = 4
MAX_LAYER_NUM_OF_FRAME = 128
MAX_NAL_UNITS_IN_LAYER = 128
AUTO_REF_PIC_COUNT = -1
UNSPECIFIED_BIT_RATE = 0

# Enums
class EVideoFormatType(c_int):
    videoFormatRGB = 1
    videoFormatRGBA = 2
    videoFormatRGB565 = 3
    videoFormatBGR = 4
    videoFormatBGRA = 5
    videoFormatABGR = 6
    videoFormatARGB = 7
    videoFormatYUV420P = 20
    videoFormatYUV422P = 21
    videoFormatYUV444P = 22
    videoFormatYV12 = 23
    videoFormatI420 = 24
    videoFormatNV12 = 25
    videoFormatNV21 = 26

class EUsageType(c_int):
    CAMERA_VIDEO_REAL_TIME = 0
    SCREEN_CONTENT_REAL_TIME = 1
    CAMERA_VIDEO_NON_REAL_TIME = 2
    INPUT_CONTENT_TYPE_ALL = 0xFF

class RC_MODES(c_int):
    RC_QUALITY_MODE = 0
    RC_BITRATE_MODE = 1
    RC_BUFFERBASED_MODE = 2
    RC_TIMESTAMP_MODE = 3
    RC_OFF_MODE = -1

class DECODING_STATE(c_int):
    dsErrorFree = 0x00
    dsFramePending = 0x01
    dsRefLost = 0x02
    dsBitstreamError = 0x04
    dsDepLayerLost = 0x08
    dsNoParamSets = 0x10
    dsDataErrorConcealed = 0x20
    dsRefListNullPtrs = 0x40
    dsInvalidArgument = 0x1000
    dsInitialOptExpected = 0x2000
    dsOutOfMemory = 0x4000
    dsDstBufNeedExpan = 0x8000

# Structures
class SSourcePicture(Structure):
    """Structure for input picture data."""
    _fields_ = [
        ("iColorFormat", c_int),
        ("iStride", c_int * 4),
        ("pData", POINTER(c_ubyte) * 4),
        ("iPicWidth", c_int),
        ("iPicHeight", c_int),
        ("uiTimeStamp", c_int64),
    ]

class SLayerBSInfo(Structure):
    """Layer bitstream info."""
    _fields_ = [
        ("uiTemporalId", c_ubyte),
        ("uiSpatialId", c_ubyte),
        ("uiQualityId", c_ubyte),
        ("eFrameType", c_int),
        ("uiLayerType", c_ubyte),
        ("iSubSeqId", c_int),
        ("iNalCount", c_int),
        ("pNalLengthInByte", POINTER(c_int)),
        ("pBsBuf", POINTER(c_ubyte)),
    ]

class SFrameBSInfo(Structure):
    """Frame bitstream info."""
    _fields_ = [
        ("iLayerNum", c_int),
        ("sLayerInfo", SLayerBSInfo * MAX_LAYER_NUM_OF_FRAME),
        ("eFrameType", c_int),
        ("iFrameSizeInBytes", c_int),
        ("uiTimeStamp", c_int64),
    ]

class SEncParamBase(Structure):
    """Basic encoder parameters."""
    _fields_ = [
        ("iUsageType", c_int),
        ("iPicWidth", c_int),
        ("iPicHeight", c_int),
        ("iTargetBitrate", c_int),
        ("iRCMode", c_int),
        ("fMaxFrameRate", c_float),
    ]

class SBufferInfo(Structure):
    """Decoder buffer info."""
    _fields_ = [
        ("iBufferStatus", c_int),
        ("uiInBsTimeStamp", c_int64),
        ("uiOutYuvTimeStamp", c_int64),
        ("UsrData", c_void_p),
    ]

class SDecodingParam(Structure):
    """Decoding parameters."""
    _fields_ = [
        ("pFileNameRestructed", c_char_p),
        ("uiCpuLoad", c_uint),
        ("uiTargetDqLayer", c_ubyte),
        ("eEcActiveIdc", c_int),
        ("bParseOnly", c_bool),
        ("sVideoProperty", c_void_p),  # Simplified for now
    ]

# Define function prototypes
def _define_encoder_functions():
    """Define encoder function prototypes."""
    # WelsCreateSVCEncoder
    _lib.WelsCreateSVCEncoder.argtypes = [POINTER(c_void_p)]
    _lib.WelsCreateSVCEncoder.restype = c_int
    
    # WelsDestroySVCEncoder  
    _lib.WelsDestroySVCEncoder.argtypes = [c_void_p]
    _lib.WelsDestroySVCEncoder.restype = None

def _define_decoder_functions():
    """Define decoder function prototypes."""
    # WelsCreateDecoder
    _lib.WelsCreateDecoder.argtypes = [POINTER(c_void_p)]
    _lib.WelsCreateDecoder.restype = c_int
    
    # WelsDestroyDecoder
    _lib.WelsDestroyDecoder.argtypes = [c_void_p]
    _lib.WelsDestroyDecoder.restype = None

# Initialize function prototypes
try:
    _define_encoder_functions()
    _define_decoder_functions()
except AttributeError as e:
    _LOGGER.error(f"Function not found in library: {e}")
    raise

class OpenH264Encoder:
    """Python wrapper for OpenH264 encoder."""
    
    def __init__(self):
        """Initialize the encoder."""
        self._encoder = c_void_p()
        self._initialized = False
        
        result = _lib.WelsCreateSVCEncoder(byref(self._encoder))
        if result != 0:
            raise RuntimeError(f"Failed to create encoder: {result}")
    
    def initialize(self, width: int, height: int, bitrate: int, 
                  framerate: float, usage_type: int = EUsageType.CAMERA_VIDEO_REAL_TIME):
        """Initialize encoder with basic parameters."""
        param = SEncParamBase()
        param.iUsageType = usage_type
        param.iPicWidth = width
        param.iPicHeight = height
        param.iTargetBitrate = bitrate
        param.iRCMode = RC_MODES.RC_BITRATE_MODE
        param.fMaxFrameRate = framerate
        
        # Get Initialize function
        initialize_func = _lib[f"?Initialize@ISVCEncoder@@QEAAHPEAU{SEncParamBase.__name__}@@@Z"]
        initialize_func.argtypes = [c_void_p, POINTER(SEncParamBase)]
        initialize_func.restype = c_int
        
        result = initialize_func(self._encoder, byref(param))
        if result != 0:
            raise RuntimeError(f"Failed to initialize encoder: {result}")
        
        self._initialized = True
        _LOGGER.info(f"Encoder initialized: {width}x{height}, {bitrate} bps, {framerate} fps")
    
    def encode_frame(self, frame_data: bytes, width: int, height: int, 
                    timestamp: int = 0) -> Tuple[bytes, int]:
        """Encode a single frame."""
        if not self._initialized:
            raise RuntimeError("Encoder not initialized")
        
        # Prepare source picture
        pic = SSourcePicture()
        pic.iColorFormat = EVideoFormatType.videoFormatI420
        pic.iPicWidth = width
        pic.iPicHeight = height
        pic.uiTimeStamp = timestamp
        
        # Set up strides
        pic.iStride[0] = width
        pic.iStride[1] = width // 2
        pic.iStride[2] = width // 2
        pic.iStride[3] = 0
        
        # Convert frame data to ctypes arrays
        frame_size = len(frame_data)
        frame_array = (c_ubyte * frame_size).from_buffer_copy(frame_data)
        
        # Set data pointers
        pic.pData[0] = cast(frame_array, POINTER(c_ubyte))
        pic.pData[1] = cast(byref(frame_array, width * height), POINTER(c_ubyte))
        pic.pData[2] = cast(byref(frame_array, width * height * 5 // 4), POINTER(c_ubyte))
        pic.pData[3] = None
        
        # Prepare output
        info = SFrameBSInfo()
        
        # Encode frame (function signature to be defined based on actual API)
        # This is a placeholder - actual implementation would call the encoder
        # result = encode_func(self._encoder, byref(pic), byref(info))
        
        # For now, return empty data and success code
        return b"", 0
    
    def __del__(self):
        """Cleanup encoder resources."""
        if hasattr(self, '_encoder') and self._encoder:
            _lib.WelsDestroySVCEncoder(self._encoder)

class OpenH264Decoder:
    """Python wrapper for OpenH264 decoder."""
    
    def __init__(self):
        """Initialize the decoder."""
        self._decoder = c_void_p()
        self._initialized = False
        
        result = _lib.WelsCreateDecoder(byref(self._decoder))
        if result != 0:
            raise RuntimeError(f"Failed to create decoder: {result}")
    
    def initialize(self):
        """Initialize decoder with default parameters."""
        param = SDecodingParam()
        param.bParseOnly = False
        
        # Initialize function would be called here
        # result = initialize_func(self._decoder, byref(param))
        
        self._initialized = True
        _LOGGER.info("Decoder initialized")
    
    def decode_frame(self, bitstream: bytes) -> Tuple[bytes, int, int]:
        """Decode a single frame."""
        if not self._initialized:
            raise RuntimeError("Decoder not initialized")
        
        # Prepare input buffer
        buffer_size = len(bitstream)
        buffer_array = (c_ubyte * buffer_size).from_buffer_copy(bitstream)
        
        # Prepare output buffer
        output_data = (POINTER(c_ubyte) * 3)()
        buffer_info = SBufferInfo()
        
        # Decode frame (placeholder implementation)
        # result = decode_func(self._decoder, buffer_array, buffer_size, 
        #                     output_data, byref(buffer_info))
        
        # For now, return empty data
        return b"", 0, 0
    
    def __del__(self):
        """Cleanup decoder resources."""
        if hasattr(self, '_decoder') and self._decoder:
            _lib.WelsDestroyDecoder(self._decoder)

class MemoryManager:
    """Utility class for managing memory buffers."""
    
    @staticmethod
    def create_buffer(size: int) -> ctypes.Array:
        """Create a ctypes buffer of specified size."""
        return (c_ubyte * size)()
    
    @staticmethod
    def copy_to_buffer(data: bytes) -> ctypes.Array:
        """Copy Python bytes to ctypes buffer."""
        size = len(data)
        buffer = (c_ubyte * size).from_buffer_copy(data)
        return buffer
    
    @staticmethod
    def buffer_to_bytes(buffer: ctypes.Array) -> bytes:
        """Convert ctypes buffer to Python bytes."""
        return bytes(buffer)

def get_openh264_version() -> str:
    """Get the OpenH264 library version."""
    try:
        # This would call the actual version function from the library
        return "2.6.0"  # Placeholder
    except Exception:
        return "Unknown"

# Test basic functionality
def test_basic_functionality():
    """Test basic encoder/decoder creation."""
    try:
        encoder = OpenH264Encoder()
        decoder = OpenH264Decoder()
        
        _LOGGER.info("Basic functionality test passed")
        return True
    except Exception as e:
        _LOGGER.error(f"Basic functionality test failed: {e}")
        return False

if __name__ == "__main__":
    # Run basic test
    logging.basicConfig(level=logging.INFO)
    success = test_basic_functionality()
    if success:
        print("OpenH264 bindings loaded successfully!")
    else:
        print("Failed to load OpenH264 bindings.")