import csv
import json
import os
from multiprocessing import Pool
from musicnn.tagger import top_tags
from musicnn.tagger import top_tags


class SongAnalyze:
    def __init__(self, modelnr, filename):
        self.modelnr = modelnr
        self.file = filename

    model_dict = {
        1: "MTT_musicnn",
        2: "MSD_musicnn",
        3: "MSD_vgg",
        4: "MTT_vgg"
    }

    def all_tag(self, n=15):
        taggers1 = top_tags(self.file, model='MTT_musicnn', topN=n)
        taggers2 = top_tags(self.file, model='MSD_musicnn', topN=n)
        taggers3 = top_tags(self.file, model='MSD_vgg', topN=n)
        taggers4 = top_tags(self.file, model="MTT_vgg", topN=n)

        tags = taggers1, taggers2, taggers3, taggers4

        return tags

    def useful_tag(self, i=15, modelnumber=2, save_tags=None):
        self.modelnr = modelnumber
        print("waffling")
        print(f"Model: {self.model_dict[self.modelnr]}, i: {i}")

        tags = top_tags(self.file, model=self.model_dict[self.modelnr], topN=i)

        if save_tags:
            with open(save_tags, 'a') as json_file:
                data = {
                    'file': os.path.basename(self.file),
                    'tags': tags
                }
                json.dump(data, json_file)
                json_file.write('\n')

        return tags


def process_folder(folder_path, model_number=1, top_tags_count=15, output_json='tags.json'):
    for filename in os.listdir(folder_path):
        if filename.endswith(".mp3"):
            file_path = os.path.join(folder_path, filename)
            print(f"Processing file: {file_path}")

            song = SongAnalyze(model_number, file_path)
            tags = song.useful_tag(top_tags_count, model_number, save_tags=output_json)
            print(f"Tags for {filename}: {tags}")


# Example usage:
folder_path = 'audio/vempire'
model_number = 1
top_tags_count = 15
output_json = 'tags.json'
process_folder(folder_path, model_number, top_tags_count, output_json)