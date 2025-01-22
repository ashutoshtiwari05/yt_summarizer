from youtube_summarizer import YouTubeSummarizer
from datetime import datetime
import os

def save_summary(result, output_dir="summaries"):
    """Save the summary to a file"""
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create filename using video title and timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c for c in result["title"] if c.isalnum() or c in (' ', '-', '_')).rstrip()
    filename = f"{safe_title}_{timestamp}.txt"
    filepath = os.path.join(output_dir, filename)
    
    # Write summary to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Video Title: {result['title']}\n")
        f.write("=" * 50 + "\n\n")
        f.write("Summary with Timestamps:\n")
        f.write("-" * 25 + "\n\n")
        f.write(result["summary"])
    
    return filepath

def main():
    print("YouTube Video Summarizer")
    print("-----------------------")
    
    youtube_url = input("Enter YouTube video URL: ")
    
    summarizer = YouTubeSummarizer()
    result = summarizer.process_video(youtube_url)
    
    if isinstance(result, dict):
        print("\nVideo Title:", result["title"])
        print("\nSummary with Timestamps:")
        print("------------------------")
        print(result["summary"])
        
        # Save to file
        output_file = save_summary(result)
        print(f"\nSummary saved to: {output_file}")
    else:
        print(result)

if __name__ == "__main__":
    main() 