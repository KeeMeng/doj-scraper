import os
import json

paragraph_count = 0
sentence_count = 0
path = "output"
for root, dirs, files in os.walk(path):
	for file in files:
		if file != ".DS_Store" and file.endswith(".json"):
			with open(os.path.join(root, file), "rb") as json_file:
				data = json.load(json_file)
				enzh = data["sentences"]["enzh"]
				if enzh != []:
					[print(i) for i in enzh]
				if data["para_aligned_status"]:
					paragraph_count += 1
				if data["sentence_aligned_status"]:
					sentence_count += 1
print()
print("paragraph aligned count: " + paragraph_count)
print("sentence aligned count: " + sentence_count)