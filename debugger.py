import os
import json

path = "output"
for root, dirs, files in os.walk(path):
	for file in files:
		if file != ".DS_Store" and file.endswith(".json"):
			with open(os.path.join(root, file), "rb") as json_file:
				data = json.load(json_file)
				enzh = data["sentences"]["enzh"]
				if enzh != []:
					[print(i) for i in enzh]