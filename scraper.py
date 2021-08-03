import re
import os
import json
import time
import requests
import datetime
from bs4 import BeautifulSoup
from argparse import ArgumentParser


def scrape(link):
	r = requests.post(link).content.decode('utf-8')

	r = re.sub("[\r\t\f\v\n]", "", r)
	r = re.sub("<[ /]*br[ /]*>", "\n", r)
	r = re.sub(" +", " ", r)
	r = re.sub("\u200b|\u3000", "", r)
	r = re.sub("<!--([\w\W]*?)-->", "", r)

	page = BeautifulSoup(r.encode("utf-8"), "html.parser")

	try:
		title = page.find_all("h2")[0].get_text()
		if "(english only)" in title.lower() or "（只有中文）" in title:
			return (None, None)
		elif title == "The request could not be satisfied.":
			# Usually when the server is busy
			print("!!! Server busy, retrying in 5 seconds: " + link)
			time.sleep(5)
			return scrape(link)

		text = ""
		# If all the content is in div and/or p
		try:
			for e in page.find("div", {"class": "pressContent"}):
				if not e.name and e.strip() and "" "************** content" not in e.strip() and e.strip not in ["完", "。", ").", "."]:
					text += e.strip() + "\n"
				elif e.name == "p":
					text += e.get_text() + "\n"
		# If all the content is not in div but some are in p
		except AttributeError:
			try:
				for e in page.find("body"):
					if not e.name and e.strip() and "" "************** content" not in e.strip() and e.strip not in ["完", "。", ").", "."]:
						text += e.strip() + "\n"
					elif e.name == "p":
						text += e.get_text() + "\n"
			# If all the content is not in div or a p (Very unlikely)
			except TypeError:
				for e in page.find("body"):
					if not e.name and e.strip() and "" "************** content" not in e.strip() and e.strip not in ["完", "。", ").", "."]:
						text += e.strip() + "\n"

	except IndexError:
		return (None, None)
	paragraphs = text.split("\n")
	return ([paragraph.strip() for paragraph in paragraphs if paragraph.strip() != ""], title)


def main():
	parser = ArgumentParser(prog="cli")
	parser.add_argument("-d", "--date", help="Starting date of press release (Inclusive)", nargs="?", default="2012-01-01")
	args = parser.parse_args()
	args_date = args.date.replace("-", "")

	if not os.path.exists("output"):
		os.makedirs("output")

	# 2021
	links = []
	index_page = BeautifulSoup(requests.post("https://www.doj.gov.hk/en/community_engagement/press/index.html").text, "html.parser")
	for press_release in index_page.find_all("a", {"href": re.compile("pr\d\.html$")}):
		if "(english only)" not in press_release.contents[0].lower():
			link = press_release.get("href")
			if int(link[:8]) >= int(args_date):
				links.append(link)

	# Archive (2012-2020)
	start_year = max(2012, int(args_date[:4]))
	for year in range(start_year, datetime.datetime.now().year):
		page = BeautifulSoup(requests.post(f"https://www.doj.gov.hk/en/archive/press_{year}.html").text, "html.parser")
		for press_release in page.find_all("a", {"href": re.compile("pr\d\.html$")}):
			if "(english only)" not in press_release.contents[0].lower():
				link = re.search("\/(\\d\\d\\d\\d\\d\\d\\d\\d_pr\\d\.html)", press_release.get("href")).group(1)
				if int(link[:8]) >= int(args_date):
					links.append(link)

	for link in links:
		print(link)
		en_link = "https://www.doj.gov.hk/en/community_engagement/press/" + link
		zh_link = en_link.replace("/en/", "/tc/")

		(en_paragraphs, en_title) = scrape(en_link)
		(zh_paragraphs, zh_title) = scrape(zh_link)
		if not en_paragraphs or not zh_paragraphs:
			print("!!! 2 languages not avaliable: " + link)
			continue

		date = link[0:-9]
		iso_date = f"{date[0:4]}-{date[4:6]}-{date[6:8]}"

		# split to sentences
		en_sentences, zh_sentences, enzh_sentences, other_sentences = [], [], [], []
		[[en_sentences.append(en_sentence.strip()) for en_sentence in en_paragraph.split(". ") if en_sentence.strip() != ""] for en_paragraph in en_paragraphs]
		for zh_paragraph in zh_paragraphs:
			for zh_sentence in zh_paragraph.split("\u3002"):
				if zh_sentence.strip() in ["」", "）", "』", "……」"]:
					zh_sentences[-1] += zh_sentence.strip()
				elif zh_sentence.strip() != "":
					zh_sentences.append(zh_sentence.strip())

		# remove enzh from en
		count = 0
		while count < len(en_sentences):
			sentence = en_sentences[count]
			try:
				zh_words = len(re.findall("[\u4e00-\u9fff]", sentence))
				all_words = len(re.findall("([\u4e00-\u9fff])|([a-zA-Z]+)", sentence))
				if zh_words / all_words > 0.05 and zh_words > 2:
					en_sentences.remove(sentence)
					count -= 1
					enzh_sentences.append(sentence)
			except ZeroDivisionError:
				# no english or chinese text, eg. numbers
				en_sentences.remove(sentence)
				count -= 1
				other_sentences.append(sentence)
			count += 1

		# remove enzh from zh
		count = 0
		while count < len(zh_sentences):
			sentence = zh_sentences[count]
			try:
				en_words = len(re.findall("[a-zA-Z]+", sentence))
				all_words = len(re.findall("([\u4e00-\u9fff])|([a-zA-Z]+)", sentence))
				if en_words / all_words > 0.05 and en_words > 2:
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
			"en_title": en_title,
			"zh_title": zh_title,
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
