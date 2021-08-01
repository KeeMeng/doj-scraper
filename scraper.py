import re
import os
import json
import requests
import datetime
from bs4 import BeautifulSoup
from argparse import ArgumentParser

def main():
	parser = ArgumentParser(prog="cli")
	parser.add_argument("-d", "--date", help="Starting date of press release", nargs="?", default="2012-01-01")
	args = parser.parse_args()

	# args_date = "20190601" # Demo date
	args_date = args.date.replace("-", "")

	# folder for json
	if not os.path.exists("output"):
		os.makedirs("output")

	# 2021
	links = []
	index_page = BeautifulSoup(requests.post("https://www.doj.gov.hk/en/community_engagement/press/index.html").text, "html.parser")
	for press_release in index_page.find_all("a", {"href": re.compile("pr\d\.html$")}):
		if "(english only)" not in press_release.contents[0].lower():
			link = press_release.get("href")
			if int(link[:8]) > int(args_date):
				links.append(link)

	# Archive
	start_year = max(2012, int(args_date[:4]))
	for year in range(start_year, datetime.datetime.now().year):
		page = BeautifulSoup(requests.post(f"https://www.doj.gov.hk/en/archive/press_{year}.html").text, "html.parser")
		for press_release in page.find_all("a", {"href": re.compile("pr\d\.html$")}):
			if "(english only)" not in press_release.contents[0].lower():
				link = re.search("\/(\\d\\d\\d\\d\\d\\d\\d\\d_pr\\d\.html)", press_release.get("href")).group(1)
				if int(link[:8]) > int(args_date):
					links.append(link)
	
	for link in links:
		# Get english text
		en_link = "https://www.doj.gov.hk/en/community_engagement/press/" + link
		page = BeautifulSoup(requests.post(en_link).content, "html.parser")

		try:
			title = page.find_all("h2")[0].get_text()
			if "(english only)" in title.lower():
				continue
			text = page.find_all("div", {"class": "pressContent"})[0].get_text()
		except IndexError:
			continue

		# Fix some characters
		text = re.sub("[^\\S \n]", "", text)
		text = re.sub(" +", " ", text)
		text = re.sub("\u200b", "", text)

		en_paragraphs = text.split("\n")
		en_paragraphs = [en_paragraph.strip() for en_paragraph in en_paragraphs if en_paragraph.strip() != ""]

		# Get chinese text
		zh_link = en_link.replace("/en/", "/tc/")
		page = BeautifulSoup(requests.post(zh_link).content, "html.parser")
		
		try:
			text = page.find_all("div", {"class": "pressContent"})[0].get_text()
		except IndexError:
			continue

		# Fix some characters
		text = re.sub("[^\\S \n]", "", text)
		text = re.sub(" +", " ", text)
		text = re.sub("\u200b", "", text)

		zh_paragraphs = text.split("\n")
		zh_paragraphs = [zh_paragraph.strip() for zh_paragraph in zh_paragraphs if zh_paragraph.strip() != ""]

		date = link[0:-9]
		iso_date = f"{date[0:4]}-{date[4:6]}-{date[6:8]}"

		# split to sentences
		en_sentences = []
		zh_sentences = []
		enzh_sentences = []
		other_sentences = []
		[[en_sentences.append(en_sentence.strip()) for en_sentence in en_paragraph.split(". ") if en_sentence.strip() != ""] for en_paragraph in en_paragraphs]
		for zh_paragraph in zh_paragraphs:
			for zh_sentence in zh_paragraph.split("\u3002"):
				if zh_sentence.strip() == "」" or zh_sentence.strip() == "）" or zh_sentence.strip() == "』" or zh_sentence.strip() == "……」":
					zh_sentences[-1] += zh_sentence.strip()
				elif zh_sentence.strip() != "":
					zh_sentences.append(zh_sentence.strip())

		# remove enzh from en
		count = 0
		while count < len(en_sentences):
			sentence = en_sentences[count]
			try:
				if len(re.findall("[\u4e00-\u9fff]", sentence)) / len(re.findall("([\u4e00-\u9fff])|([a-zA-Z]+)", sentence)) > 0.05 and len(re.findall("[\u4e00-\u9fff]", sentence)) > 2:
					en_sentences.remove(sentence)
					count -= 1
					enzh_sentences.append(sentence)
			except ZeroDivisionError:
				en_sentences.remove(sentence)
				count -= 1
				other_sentences.append(sentence)
			count += 1

		# remove enzh from zh
		count = 0
		while count < len(zh_sentences):
			sentence = zh_sentences[count]
			try:
				if len(re.findall("[a-zA-Z]+", sentence)) / len(re.findall("([\u4e00-\u9fff])|([a-zA-Z]+)", sentence)) > 0.05 and len(re.findall("[a-zA-Z]+", sentence)) > 2:
					zh_sentences.remove(sentence)
					count -= 1
					enzh_sentences.append(sentence)
			except ZeroDivisionError:
				zh_sentences.remove(sentence)
				count -= 1
				other_sentences.append(sentence)
			count += 1

		data = {
			"en_url": en_link,
			"zh_url": zh_link,
			"category": "Press Release",
			"title": title,
			"release_date": iso_date,
			"para_aligned_status": len(en_paragraphs) == len(zh_paragraphs),
			"sentence_aligned_status": len(en_sentences) == len(zh_sentences),
			"contents": {
				"en": en_paragraphs,
				"zh": zh_paragraphs
			},
			"sentences": {
				"en": en_sentences,
				"zh": zh_sentences,
				"enzh": enzh_sentences,
				"others": other_sentences
			}
		}

		with open(f"output/{link}.json", "w") as json_file:
			json.dump(data, json_file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
	main()
