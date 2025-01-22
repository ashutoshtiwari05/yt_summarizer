import gradio as gr
from youtube_summarizer import YouTubeSummarizer

# Initialize the summarizer once
summarizer = YouTubeSummarizer()

def process_youtube_url(url):
    """Process YouTube URL and return summary"""
    try:
        result = summarizer.process_video(url)
        if isinstance(result, dict):
            return result['summary']  # Now contains markdown with clickable links
        return result
    except Exception as e:
        return f"Error: {str(e)}"

# Create custom CSS
custom_css = """
.summary-box {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    padding: 20px;
    background-color: #1a1a1a;  /* Dark background */
    border-radius: 8px;
    color: #ffffff;  /* White text */
}
.summary-box h1 {
    color: #ffffff;  /* White headers */
    font-size: 24px;
    margin-bottom: 20px;
    border-bottom: 1px solid #333;
    padding-bottom: 10px;
}
.summary-box a {
    color: #66b3ff;  /* Light blue links */
    text-decoration: none;
    font-weight: bold;
}
.summary-box a:hover {
    color: #99ccff;  /* Lighter blue on hover */
    text-decoration: underline;
}
.summary-box ul {
    list-style-type: none;
    padding-left: 0;
}
.summary-box li {
    margin-bottom: 10px;
    padding-left: 20px;
    position: relative;
}
.summary-box li:before {
    content: "•";
    position: absolute;
    left: 0;
    color: #66b3ff;  /* Light blue bullets */
}
"""

# Create Gradio interface
demo = gr.Interface(
    fn=process_youtube_url,
    inputs=gr.Textbox(
        label="YouTube URL",
        placeholder="Enter YouTube video URL...",
        lines=1
    ),
    outputs=gr.Markdown(
        label="Summary",
        elem_classes=["summary-box"]
    ),
    title="YouTube Video Summarizer",
    description="Enter a YouTube URL to get a timestamped summary of the video content. Click on timestamps to jump to that point in the video.",
    examples=[
        ["https://www.youtube.com/watch?v=2OCVIg4De50"],
        ["https://www.youtube.com/shorts/2OCVIg4De50"]
    ],
    theme=gr.themes.Soft(),
    css=custom_css
)

if __name__ == "__main__":
    demo.launch(share=True) 