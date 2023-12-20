import streamlit as st
import assemblyai as aai
import tempfile
import os

# Set your AssemblyAI API key
aai.settings.api_key = "dd1c2ed264744d769e3d24321a1d4014"
transcriber = aai.Transcriber()

def main():
    st.markdown("<h1 style='text-align: center;'>Subtitle Generator Web App</h1>", unsafe_allow_html=True)
    
    # File upload
    file = st.file_uploader("Select any video or audio file to get subtitles", type=["mp3", "wav", "mp4"])
    
    if file is not None:
        # Save the uploaded file to a temporary location
        temp_file_path = save_uploaded_file(file)
        
        # Transcribe the audio file
        transcript = transcribe_audio(temp_file_path)
        
        # Display subtitles in the terminal
        st.subheader("Generated Subtitles:")
        st.code(transcript.export_subtitles_srt(), language="text")
        
        # Save subtitles to a file
        save_subtitles_to_file(transcript.export_subtitles_srt(), "generated_subtitles.srt")
        st.success("Subtitles saved to 'generated_subtitles.srt'")
        
def save_uploaded_file(file):
    # Save the uploaded file to a temporary location
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path = temp_file.name
    temp_file.write(file.read())
    temp_file.close()
    return temp_file_path

def transcribe_audio(file_path):
    # Transcribe the audio file using AssemblyAI
    st.spinner("Transcribing...")
    transcript = transcriber.transcribe(file_path)
    st.success("Transcription complete!")
    return transcript

def save_subtitles_to_file(subtitles, filename):
    # Save subtitles to a file
    with open(filename, "w") as file:
        file.write(subtitles)

if __name__ == "__main__":
    main()
