from google import genai
import os

client = genai.Client(api_key="AIzaSyDnAgeubwIn7tTlmu7Ai-xgHjnPuDL1bmg")

models = client.models.list()
for m in models:
    print(m.name)