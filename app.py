import streamlit as st
import whisper
import tempfile
import os

# Timestamp format karne ka function
def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millisecs:03}"

@st.cache_resource
def load_model():
    return whisper.load_model("base")

st.title("🎬 AI Subtitle & Audio-to-Text Generator")
st.write("Apna Video ya Movie ka Audio (MP3) upload karein aur AI se automatically subtitles (SRT) banwayein.")

model = load_model()

# Yahan Audio aur Video dono formats allow kar diye hain
uploaded_file = st.file_uploader("File upload karein (MP3, WAV, MP4, MOV)", type=["mp3", "wav", "m4a", "mp4", "mov"])

if uploaded_file is not None:
    # File ka extension nikalna (taaki system ko pata chale ye audio hai ya video)
    file_extension = os.path.splitext(uploaded_file.name)[1]
    
    # UI mein file play karna (Audio hai toh audio player, video hai toh video player)
    if file_extension.lower() in [".mp4", ".mov"]:
        st.video(uploaded_file)
    else:
        st.audio(uploaded_file)
    
    if st.button("Generate Subtitles"):
        with st.spinner("AI aapki file ko sun raha hai... Movie/Badi file me 5-10 minute lag sakte hain."):
            # File ko temporary save karna uske original extension ke sath
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name

            try:
                # Whisper direct audio/video se text nikalega
                result = model.transcribe(temp_file_path)

                srt_content = ""
                for i, segment in enumerate(result["segments"]):
                    start_time = format_timestamp(segment["start"])
                    end_time = format_timestamp(segment["end"])
                    text = segment["text"].strip()
                    
                    srt_content += f"{i + 1}\n"
                    srt_content += f"{start_time} --> {end_time}\n"
                    srt_content += f"{text}\n\n"

                st.success("Subtitles successfully generate ho gaye!")
                
                st.download_button(
                    label="📥 Download .SRT File",
                    data=srt_content,
                    file_name="subtitles.srt",
                    mime="text/plain"
                )
                
                st.text_area("Preview Subtitles:", srt_content, height=300)
            except Exception as e:
                st.error(f"Error: {e}. Code fail ho gaya.")
            finally:
                if os.path.exists(temp_file_path):
                    os.path.remove(temp_file_path)
                  
