import yt_dlp
import whisper
import torch
from transformers import pipeline
from pytube import YouTube
import os
from pathlib import Path

class YouTubeSummarizer:
    def __init__(self, model_dir="models"):
        """Initialize with model caching"""
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        # Initialize the whisper model for transcription with caching
        print("Loading Whisper model...")
        self.transcription_model = self._load_whisper_model()
        
        # Initialize the summarization pipeline with caching
        print("Loading summarization model...")
        self.summarizer = self._load_summarizer_model()
    
    def _load_whisper_model(self):
        """Load Whisper model with caching"""
        cache_dir = self.model_dir / "whisper"
        cache_dir.mkdir(exist_ok=True)
        return whisper.load_model("base", download_root=str(cache_dir))
    
    def _load_summarizer_model(self):
        """Load summarization model with caching"""
        cache_dir = self.model_dir / "summarizer"
        cache_dir.mkdir(exist_ok=True)
        
        # Force CPU for summarization to avoid MPS issues
        device = "cpu"
        
        print(f"Loading summarization model on {device}...")
        return pipeline(
            "text2text-generation",
            model="google/flan-t5-large",
            device=device,
            torch_dtype=torch.float32,
            model_kwargs={"cache_dir": str(cache_dir)}
        )
    
    def _get_video_info(self, youtube_url):
        """Get video information using yt-dlp as fallback"""
        try:
            # First try with pytube
            yt = YouTube(youtube_url)
            return {
                "title": yt.title,
                "url": youtube_url
            }
        except Exception as e:
            # Fallback to yt-dlp
            try:
                with yt_dlp.YoutubeDL() as ydl:
                    info = ydl.extract_info(youtube_url, download=False)
                    return {
                        "title": info.get('title', 'Unknown Title'),
                        "url": youtube_url
                    }
            except Exception as e:
                raise Exception(f"Failed to get video info: {str(e)}")

    def download_audio(self, youtube_url):
        """Download audio from YouTube video"""
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'temp_audio.%(ext)s'
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            return 'temp_audio.mp3'
        except Exception as e:
            raise Exception(f"Failed to download audio: {str(e)}")

    def transcribe_audio(self, audio_path):
        """Transcribe audio file and return segments with timestamps"""
        try:
            print("Loading audio file...")
            # Add progress indicators
            print("Starting transcription (this may take a while on CPU)...")
            result = self.transcription_model.transcribe(
                audio_path,
                fp16=False,  # Disable FP16 to avoid warnings
                verbose=True  # Show progress
            )
            print("Transcription completed!")
            return result["segments"]
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")

    def format_time(self, seconds):
        """Convert seconds to HH:MM:SS format"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

    def _generate_section_title(self, text):
        """Generate a section title from text"""
        try:
            prompt = "Generate a very short (3-5 words) title that describes this content: " + text[:500]
            response = self.summarizer(
                prompt,
                max_length=20,  # Shorter max length for titles
                min_length=5,
                do_sample=True,
                temperature=0.3,
                num_beams=2,
                truncation=True
            )
            title = response[0]['generated_text'].strip()
            return title.title() if title else "Key Points"
        except Exception as e:
            print(f"Title generation failed: {str(e)}")
            return "Key Points"

    def _create_youtube_timestamp_link(self, video_url, seconds):
        """Create a clickable YouTube timestamp link"""
        # Extract video ID from URL
        if "youtu.be" in video_url:
            video_id = video_url.split("/")[-1].split("?")[0]
        else:
            video_id = video_url.split("v=")[1].split("&")[0]
        
        timestamp = int(seconds)
        return f"https://youtu.be/{video_id}?t={timestamp}"

    def generate_summary(self, segments, video_url):
        """Generate summary from transcribed segments"""
        print("\nProcessing transcript segments...")
        
        # For very short videos, process as a single section
        total_duration = segments[-1]["end"] if segments else 0
        is_short = total_duration < 120  # Less than 2 minutes
        
        # Combine all text for processing
        full_text = " ".join(segment["text"].strip() for segment in segments)
        
        if not full_text.strip():
            return "No transcription available to summarize."
        
        try:
            if is_short:
                print("Processing short video as single section...")
                # Generate title for the content
                section_title = self._generate_section_title(full_text)
                
                # Generate summary points
                prompt = (
                    "Extract 2-3 main points from this text. "
                    "Format as clear, concise bullet points: " + full_text
                )
                
                summary = self.summarizer(
                    prompt,
                    max_length=200,
                    min_length=50,
                    do_sample=True,
                    temperature=0.3,
                    num_beams=4,
                    no_repeat_ngram_size=2,
                    truncation=True
                )
                
                if not summary or not summary[0]['generated_text'].strip():
                    return "Could not generate summary points."
                
                # Format the summary
                formatted_summary = [
                    "# Video Summary and Key Points\n",
                    f"### {section_title}\n"
                ]
                
                # Process each point
                points = [p.strip() for p in summary[0]['generated_text'].split('\n')]
                points = [p.lstrip('•-* ') for p in points if p.strip()]
                
                # Add timestamp links
                start_time = self.format_time(0)  # Start from beginning
                timestamp_link = self._create_youtube_timestamp_link(video_url, 0)
                
                for point in points:
                    if point:
                        formatted_summary.append(f"• {point} [{start_time}]({timestamp_link})")
                
                return "\n".join(formatted_summary)
                
            else:
                # Original logic for longer videos
                sections = []
                current_section = {
                    "text": "",
                    "start": segments[0]["start"] if segments else 0,
                    "end": 0,
                    "segments": []
                }
                
                for segment in segments:
                    # Start new section every ~2 minutes
                    if segment["start"] - current_section["start"] > 120:
                        if current_section["segments"]:
                            sections.append(current_section)
                        current_section = {
                            "text": "",
                            "start": segment["start"],
                            "end": segment["end"],
                            "segments": []
                        }
                    
                    current_section["text"] += segment["text"].strip() + " "
                    current_section["end"] = segment["end"]
                    current_section["segments"].append(segment)
                
                # Add the last section
                if current_section["segments"]:
                    sections.append(current_section)
                
                print(f"\nIdentified {len(sections)} major sections")
                final_summary = []
                
                # Process each section
                for i, section in enumerate(sections, 1):
                    try:
                        print(f"\nProcessing section {i}/{len(sections)}...")
                        
                        # Generate section title
                        section_title = self._generate_section_title(section["text"])
                        
                        # Generate key points for the section
                        prompt = f"Extract 2-3 key points from this text, format as bullet points: {section['text']}"
                        summary = self.summarizer(
                            prompt,
                            max_length=150,
                            min_length=50,
                            do_sample=True,  # Enable sampling
                            temperature=0.3,
                            num_beams=4,
                            no_repeat_ngram_size=2,
                            truncation=True
                        )
                        
                        if summary and len(summary) > 0:
                            summary_text = summary[0]['generated_text'].strip()
                            if summary_text:
                                # Format timestamps for the section with clickable link
                                start_time = self.format_time(section["start"])
                                timestamp_link = self._create_youtube_timestamp_link(video_url, section["start"])
                                
                                # Format the section with title and key points
                                formatted_section = f"### {section_title}\n"
                                
                                # Split key points and add timestamps
                                points = [p for p in summary_text.split('\n') if p.strip()]
                                for point in points:
                                    point = point.strip()
                                    if point:
                                        # Remove bullet points if present and clean up
                                        point = point.lstrip('•-* ')
                                        formatted_section += f"• {point} [{start_time}]({timestamp_link})\n"
                                
                                if points:  # Only add section if we have points
                                    final_summary.append(formatted_section)
                                    print(f"Successfully summarized section {i}")
                    
                    except Exception as e:
                        print(f"Warning: Failed to summarize section {i}: {str(e)}")
                        continue
                
                if not final_summary:
                    return "No summary could be generated."
                
                # Add a header for the entire summary
                header = "# Video Summary and Key Points\n\n"
                
                return header + "\n".join(final_summary)
                
        except Exception as e:
            print(f"Error in summary generation: {str(e)}")
            # Fallback to a simple summary
            try:
                prompt = "Summarize this text briefly: " + full_text[:1000]  # Limit text length
                summary = self.summarizer(
                    prompt,
                    max_length=100,
                    min_length=30,
                    do_sample=False,
                    truncation=True
                )
                
                if summary and summary[0]['generated_text'].strip():
                    return (
                        "# Video Summary\n\n"
                        f"• {summary[0]['generated_text'].strip()} "
                        f"[{self.format_time(0)}]({self._create_youtube_timestamp_link(video_url, 0)})"
                    )
                
            except:
                pass
            
            return "Could not generate summary. Please try again."

    def process_video(self, youtube_url):
        """Process YouTube video and return summary with timestamps"""
        try:
            # Get video info
            video_info = self._get_video_info(youtube_url)
            video_title = video_info["title"]
            
            print(f"Processing video: {video_title}")
            print("Downloading audio...")
            audio_path = self.download_audio(youtube_url)
            
            print("Transcribing audio...")
            segments = self.transcribe_audio(audio_path)
            
            print("Generating summary...")
            summary = self.generate_summary(segments, youtube_url)
            
            # Clean up temporary audio file
            os.remove(audio_path)
            
            return {
                "title": video_title,
                "summary": summary
            }
            
        except Exception as e:
            return f"Error processing video: {str(e)}" 