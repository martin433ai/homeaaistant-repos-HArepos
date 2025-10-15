# OpenH264 Video Processing Integration for Home Assistant

This repository contains a Home Assistant custom integration that provides H.264 video encoding and decoding capabilities using the OpenH264 library, specifically designed for security cameras and video streaming applications.

## Features

- **Real-time H.264 encoding/decoding** using the OpenH264 library
- **Security camera optimization** with bitrate adaptation and quality control
- **Stream transcoding** between different H.264 profiles and resolutions
- **Multi-threading support** for concurrent video processing
- **Home Assistant services** for video processing automation
- **Statistics and monitoring** for encoding/decoding performance
- **Configurable quality presets** for different use cases

## Installation

### Prerequisites

- Home Assistant 2023.1 or newer
- Python 3.10 or newer
- OpenH264 library (included in the integration)

### Manual Installation

1. Clone this repository to your `custom_components` directory:
```bash
cd /config/custom_components
git clone https://github.com/martin433ai/homeaaistant-repos-HArepos.git
```

2. Copy the integration files:
```bash
cp -r homeaaistant-repos-HArepos/custom_components/openh264_video /config/custom_components/
```

3. Restart Home Assistant

## Configuration

### UI Configuration

1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "OpenH264 Video Processing"
4. Follow the configuration wizard

### YAML Configuration

```yaml
openh264_video:
  target_bitrate: 2000000  # 2 Mbps
  max_framerate: 30.0
  resolution: "1920x1080"
  profile: "baseline"
  encoder_threads: 4
```

## Services

The integration provides several services for video processing:

### `openh264_video.encode_frame`
Encode a single frame to H.264 format.

```yaml
service: openh264_video.encode_frame
data:
  frame_data: "base64_encoded_frame_data"
  width: 1920
  height: 1080
  format: "yuv420"
  quality: 23
```

### `openh264_video.decode_frame`
Decode H.264 bitstream to raw frame data.

```yaml
service: openh264_video.decode_frame
data:
  bitstream_data: "base64_encoded_h264_data"
  output_format: "yuv420"
```

### `openh264_video.transcode_stream`
Transcode video streams with different parameters.

```yaml
service: openh264_video.transcode_stream
data:
  input_stream: "rtsp://camera.local/stream1"
  output_stream: "rtmp://server.local/stream1"
  target_bitrate: 1500000
  target_resolution: "1280x720"
```

## Use Cases

### Security Camera Optimization

```yaml
# Optimize for security cameras with motion detection
openh264_video:
  target_bitrate: 1500000  # 1.5 Mbps for good quality
  max_framerate: 15.0      # Lower framerate for storage efficiency
  resolution: "1280x720"   # Balance between quality and bandwidth
  profile: "baseline"      # Maximum compatibility
  quality_preset: "fast"   # Real-time encoding
```

### High-Quality Recording

```yaml
# High-quality recording setup
openh264_video:
  target_bitrate: 8000000  # 8 Mbps for high quality
  max_framerate: 30.0      # Full framerate
  resolution: "1920x1080"  # Full HD
  profile: "high"          # Best compression
  quality_preset: "slow"   # Better compression
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Acknowledgments

- [OpenH264](https://www.openh264.org/) by Cisco Systems
- [Home Assistant](https://www.home-assistant.io/) community
