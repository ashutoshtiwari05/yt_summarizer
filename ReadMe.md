# YouTube Video Summarizer

A powerful tool that automatically generates timestamped summaries of YouTube videos using AI. The tool transcribes the video audio and creates a structured summary with clickable timestamps that link directly to the relevant parts of the video.

## Features

- 🎥 Supports both long videos and YouTube Shorts
- 🔊 High-quality audio transcription using OpenAI's Whisper model
- 📝 Intelligent summarization using Google's FLAN-T5 model
- ⌚ Clickable timestamps that jump to specific video sections
- 🎯 Section-based summaries for longer videos
- 💾 Local model caching for faster subsequent runs
- 🌐 Web interface using Gradio
- 🔖 Browser bookmarklet for quick access

## Requirements

- Python 3.10 or higher
- Conda package manager
- FFmpeg
- Internet connection for downloading videos and models

## Available Commands

- `make setup` - Create conda environment and install dependencies
- `make run` - Run the CLI version
- `make serve` - Start the web interface
- `make clean` - Remove environment and generated files
- `make update` - Update existing environment
- `make all` - Setup, configure and run the application
- `make help` - Show help message

## Technical Details

- Uses OpenAI's Whisper model for accurate speech-to-text transcription
- FLAN-T5-large model for high-quality text summarization
- yt-dlp for reliable YouTube video downloading
- Supports CPU, CUDA (NVIDIA), and MPS (Apple Silicon) devices
- Automatic device detection and optimization
- Fallback mechanisms for robust operation

## Known Issues

1. First run takes longer due to model downloads
2. Some YouTube Shorts might need multiple attempts
3. Very long videos (>1 hour) might need more processing time
4. Share functionality might not work behind corporate firewalls

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your license information here]

## Acknowledgments

- OpenAI Whisper for transcription
- Google's FLAN-T5 for summarization
- Hugging Face for model hosting
- Gradio for the web interface
- yt-dlp for video downloading

## Support

If you encounter any issues or have questions:
1. Check the known issues section
2. Open an issue on GitHub
3. Provide the video URL and error message for better support