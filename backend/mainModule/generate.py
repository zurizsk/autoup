import sys
from openai import OpenAI
import csv

client = OpenAI()


def read_msccn_output():
    with open('../zupload36/tags.csv', 'r') as file:
        reader = csv.reader(file)
        return str(list(reader))


prompt = read_msccn_output()
print(prompt)
# response = client.chat.completions.create(
#     model='gpt-3.5-turbo',
#     messages=[
#         {"role": "system", "content": '1) turn output lower case! 2) create rap type beat titles from appended tags, default '
#                                       'title format is:[FREE] (fitting artist1) x (fitting artist2) x (fitting '
#                                       'artist3) type beat '"(short cool title)"' (prod. v-empire) use top 100 artists'
#                                       '3) LOOK UP TOP 100 ARTISTS!! DONT JUST USE TAGS'},
#
#         {"role": "user", "content": prompt}
#     ]
# )
# print(response)
