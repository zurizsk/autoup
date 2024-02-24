import sys
from openai import OpenAI
import csv
import whisper
import json

client = OpenAI()


import subprocess

def convert_video_to_audio(input_file, output_file, sample_rate=44100, channels=2):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-vn',
        '-acodec', 'libmp3lame',  # Use libmp3lame for mp3 encoding
        '-ar', str(sample_rate),
        '-ac', str(channels),
        output_file
    ]

    subprocess.run(command)


# Example usage
input_video = 'vid.mp4'
output_audio = 'audio.mp3'


def transcribe(audio_path="audio.mp3"):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    print(result["text"])
    return result["text"]


def convert_and_transcribe(video_path='vid.mp4'):
    convert_video_to_audio(video_path, output_audio)
    return transcribe(output_audio)


def save_transcription_to_json(text, json_file='transcription.json'):
    with open(json_file, 'w') as f:
        json.dump({'transcription': text}, f)


# transcription_text = convert_and_transcribe(input_video)
# save_transcription_to_json(transcription_text)


def read_msccn_output():

    with open('../zupload36/tags.csv', 'r') as file:
        reader = csv.reader(file)
        return str(list(reader))


def generate_title_aspect_suggestions(file_name='transcription.json'):
    f = open(file_name, 'r')
    text = json.load(f)['transcription']
    completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": "you are supposed to generate 5 aspects of the given, it will be used to allow "
                                      "the user to select aspects to insert into the title. give broad terms such as "
                                      "but not limited to: drama, challenge, comedy, etc. based on the transcript."
                                      "an aspect is usually one or two words describing a theme or topic."
                                      "the following transcript."},
        {"role": "user", "content": "Here is a transcript: " + text}
      ]
    )
    return completion


def generate_title_from_transcript(file_name='transcription.json'):
    f = open(file_name, 'r')
    text = json.load(f)['transcription']
    completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": "You are supposed to generate 5 title for a youtube video based on the "
                                      "following transcript."},
        {"role": "user", "content": "Make the titles short and intriguing. max 6 words. bring in the drama here is a "
                                    "transcript: " + text}
      ]
    )
    return completion


print(generate_title_aspect_suggestions('transcription.json'))
print(generate_title_from_transcript('transcription.json'))


