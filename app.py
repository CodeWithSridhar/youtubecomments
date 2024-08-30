import os
import googleapiclient.discovery
import pandas as pd
import streamlit as st
from fpdf import FPDF

def get_comments(video_id, api_key):
    # Set up the API client
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)

    # Initialize an empty list to hold comments
    comments = []

    # Retrieve comments
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100  # Maximum is 100
    )
    response = request.execute()

    while response:
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textOriginal']
            comments.append(comment)

        # Check if there is a next page token, indicating more comments to fetch
        if 'nextPageToken' in response:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                pageToken=response['nextPageToken']
            )
            response = request.execute()
        else:
            break

    return comments

def save_comments_to_csv(comments, filename):
    df = pd.DataFrame(comments, columns=['Comment'])
    df.to_csv(filename, index=False)
    return filename

def save_comments_to_pdf(comments, filename):
    pdf = FPDF()
    pdf.add_page()

    # Specify a font path that is available on your system
    pdf.add_font('ArialUnicodeMS', '', 'C:\\Windows\\Fonts\\ARIALUNI.TTF', uni=True)
    pdf.set_font("ArialUnicodeMS", size=12)

    for comment in comments:
        pdf.multi_cell(0, 10, comment)

    pdf.output(filename)
    return filename

def main():
    st.title("YouTube Comment Extractor")

    api_key = st.text_input("Enter Your YouTube API Key", type="password")
    video_ids_input = st.text_area("Enter YouTube Video IDs (comma-separated)")

    if st.button("Fetch Comments"):
        if api_key and video_ids_input:
            video_ids = [vid.strip() for vid in video_ids_input.split(",")]

            for video_id in video_ids:
                comments = get_comments(video_id, api_key)

                if comments:
                    st.success(f"Comments fetched successfully for video ID: {video_id}")

                    # Save comments to CSV
                    csv_filename = f"youtube_comments_{video_id}.csv"
                    csv_file = save_comments_to_csv(comments, csv_filename)
                    st.download_button(
                        label=f"Download Comments as CSV for {video_id}",
                        data=open(csv_file, "rb").read(),
                        file_name=csv_filename,
                        mime="text/csv"
                    )

                    # Save comments to PDF
                    pdf_filename = f"youtube_comments_{video_id}.pdf"
                    pdf_file = save_comments_to_pdf(comments, pdf_filename)
                    st.download_button(
                        label=f"Download Comments as PDF for {video_id}",
                        data=open(pdf_file, "rb").read(),
                        file_name=pdf_filename,
                        mime="application/pdf"
                    )
                else:
                    st.error(f"No comments found for video ID: {video_id}")
        else:
            st.warning("Please enter both API Key and Video IDs.")

st.markdown('<p style="text-align: center;"><img src="https://www.gstatic.com/youtube/img/branding/youtubelogo/svg/youtubelogo.svg" alt="Logo" width="300"></p>', unsafe_allow_html=True)

# Sidebar content
st.sidebar.image("https://www.mygov.in/sites/all/themes/mygov/front_assets/images/logo.svg", width=100)

st.sidebar.markdown(
    """
    <div style="background-color: #003366; padding: 9px; border-radius: 9px; text-align: center;">
        <h3 style="color: white;">🌟  Welcome to the Portal of Youtube Comment Extractor 
        🌟</h3>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("### Status")
st.sidebar.markdown("<div style='font-size: 24px;'>🟢 Online</div>", unsafe_allow_html=True)

st.sidebar.title("About")
st.sidebar.info("""
    Welcome to the **YouTube** comment extractor.
    This tool helps in extracting comments from YouTube Video ID in CSV format.
""")

st.sidebar.header("👩‍💼 Developer Details")
st.sidebar.markdown("""
    <div style='line-height: 1.6;'>
        <strong>Developed by:</strong> <br> Analytics Team (MyGov) <br><br>
        <strong>Contact Us:</strong> <a href='mailto:analytics_team@mygov.in'>@analytics_team_mygov</a>
    </div>
""", unsafe_allow_html=True)

st.sidebar.subheader("🔗 Useful Links")
st.sidebar.markdown("""
    - [Project Documentation](https://www.example.com/documentation)
    - [Source Code](https://www.example.com/source-code)
    - [Report Issue](https://www.example.com/report-issue)
""")

st.sidebar.subheader("📅 Latest Updates")
st.sidebar.markdown("""
    - **Version 1.0**: Initial release with scrapper features.
    - **Version 1.1**: Added csv download format.
    - **Version 1.2**: Improved user interface and performance.
""")
if __name__ == "__main__":
    main()
