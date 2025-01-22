javascript:(function(){
    // Get the current YouTube URL
    var videoUrl = window.location.href;
    
    // Check if we're on a YouTube page
    if (videoUrl.includes('youtube.com/') || videoUrl.includes('youtu.be/')) {
        // Open the Gradio interface in a new window with the current URL
        var gradioUrl = 'http://localhost:7860/?url=' + encodeURIComponent(videoUrl);
        window.open(gradioUrl, 'YouTubeSummarizer', 'width=800,height=600');
    } else {
        alert('Please use this bookmarklet on a YouTube video page.');
    }
})(); 