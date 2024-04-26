from openai import OpenAI
import csv
import whisper
import json
import subprocess

client = OpenAI()


def load_transcription(file_name):
    f = open(file_name, 'r')
    return json.load(f)['transcription']


class Description:
    def __init__(self, description_text=None, file_name='transcription.json'):
        self.file_name = file_name
        self.transcription = load_transcription(self.file_name)
        if description_text is None:
            self.description_text = self.generate_description()
        else:
            self.description_text = description_text

    def generate_description(self):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are supposed to generate a description for a youtube "
                                              "video based on the following transcript."},
                {"role": "user", "content": "Make the description intriguing. max 100 words. bring in the "
                                            "drama here is a transcript: " + self.transcription}
            ]
        )
        return response.choices[0].message.content

    def get_description(self):
        return self.description_text


class Title:
    def __init__(self, file_name='transcription.json'):
        self.file_name = file_name
        self.transcription = load_transcription(self.file_name)
        self.title_text = self.generate_titles()
        self.aspect_text = self.generate_aspect_suggestions()

    def generate_titles(self):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are supposed to generate 5 titles for a youtube video based on the "
                                              "following transcript."},
                {"role": "user", "content": "Make the titles short and intriguing. max 6 words. bring in the drama"
                                            "here is a transcript: " + self.transcription}
            ]
        )
        return response.choices[0].message.content

    def generate_aspect_suggestions(self):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "you are supposed to generate 5 aspects of the given transcript, "
                                              "it will be used to allow insert into the title. give broad terms "
                                              "such as but not limited to: drama, challenge, comedy, etc. based on the "
                                              "transcript. an aspect is usually one or two words describing a theme "
                                              "or topic. the following transcript."},
                {"role": "user", "content": "Here is a transcript: " + self.transcription}
            ]
        )
        return response.choices[0].message.content

    def generate_title_from_aspects(self):
        if self.aspect_text is None:
            self.aspect_text = self.generate_aspect_suggestions()
        else:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are supposed to generate 5 titles for a "
                                                  "youtube video based on the following transcript."},
                    {"role": "user", "content": "Make the titles short and intriguing. max 6 words. bring in the "
                                                "following aspects: " + self.aspect_text +
                                                "here is a transcript: " + self.transcription}
                ]
            )
            return response.choices[0].message.content

    def get_aspect_suggestions(self):
        return type(self.aspect_text)

    def get_title(self):
        return self.title_text


class Tags:
    def __init__(self, file_name='transcription.json'):
        self.file_name = file_name
        self.transcription = load_transcription(self.file_name)
        self.tags_text = self.generate_tags()

    def generate_tags(self):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "you are supposed to generate 20 tags appropriate for a youtube video "
                                              "based on the given transcript. "},
                {"role": "user", "content": "Here is a transcript: " + self.transcription}
            ]
        )
        return response.choices[0].message.content

    def get_tags(self):
        return self.tags_text


class Video:
    def __init__(self, title=None, description=None, tags=None, aspect=None, file_name='transcription.json'):
        self.file_name = file_name
        if title is None:
            self.title = Title(file_name).get_title()
        else:
            self.title = title

        if aspect is None:
            self.aspect = Title().get_aspect_suggestions()
        else:
            self.aspect = aspect

        if description is None:
            self.description = Description(file_name).get_description()
        else:
            self.description = description

        if tags is None:
            self.tags = Tags(file_name).get_tags()
        else:
            self.tags = tags

    def get_video(self):
        return self.title, self.description, self.tags, self.aspect


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
            {"role": "system", "content": "you are supposed to generate 5 aspects of the given transcript, it will be "
                                          "used to allow the user to select aspects to insert into the title. "
                                          "give broad terms such as "
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
            {"role": "system", "content": "You are supposed to generate 5 titles for a youtube video based on the "
                                          "following transcript."},
            {"role": "user",
             "content": "Make the titles short and intriguing. max 6 words. here is a "
                        "transcript: " + text}
        ]
    )
    return completion


def generate_description_from_transcript(file_name='transcription.json'):
    f = open(file_name, 'r')
    text = json.load(f)['transcription']
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are supposed to generate a description for a youtube video based on the "
                                          "following transcript."},
            {"role": "user", "content": "Make the description intriguing. max 100 words. bring in the drama here is a "
                                        "transcript: " + text}
        ]
    )
    return completion


input_video = 'I tried using AI. It scared me.mp4'
output_audio = 'audio.mp3'

transcription_text = convert_and_transcribe(input_video)
save_transcription_to_json(transcription_text)

v1 = Video()
print(v1.get_video())













