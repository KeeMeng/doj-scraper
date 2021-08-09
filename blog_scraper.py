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
		if title == "The request could not be satisfied.":
			print("!!! Server busy")

		text = ""
		# If all the content is in div and/or p
		try:
			for e in page.find("div", {"class": "blogContent"}):
				if not e.name and e.strip() and "" "************** content" not in e.strip() and e.strip() not in ["完", "。", ").", "."]:
					text += e.strip() + "\n"
				elif e.name == "p" and e.get_text() not in ["完", "。", ").", "."]:
					text += e.get_text() + "\n"
		# If all the content is not in div but some are in p
		except TypeError:
			try:
				for e in page.find("body"):
					if not e.name and e.strip() and "" "************** content" not in e.strip() and e.strip() not in ["完", "。", ").", "."]:
						text += e.strip() + "\n"
					elif e.name == "p" and e.get_text() not in ["完", "。", ").", "."]:
						text += e.get_text() + "\n"
			# If all the content is not in div or a p (Very unlikely)
			except TypeError:
				for e in page.find("body"):
					if not e.name and e.strip() and "" "************** content" not in e.strip() and e.strip() not in ["完", "。", ").", "."]:
						text += e.strip() + "\n"

	except IndexError:
		return (None, None)
	paragraphs = text.split("\n")
	return ([paragraph.strip() for paragraph in paragraphs if paragraph.strip() not in ["完", "。", ").", ".", "", "Ends"]], title)


def main():
	parser = ArgumentParser(prog="cli")
	parser.add_argument("-d", "--date", help="Starting date of press release (Inclusive)", nargs="?", default="2012-01-01")
	args = parser.parse_args()
	args_date = args.date.replace("-", "")

	if not os.path.exists("blog_output"):
		os.makedirs("blog_output")

	links = []
	index_page = BeautifulSoup(requests.post("https://www.doj.gov.hk/en/community_engagement/sj_blog/blog_archives.html").text, "html.parser")
	for press_release in index_page.find_all("a", {"href": re.compile("\d_blog1\.html$")}):
		link = press_release.get("href")
		if int(link[:8]) >= int(args_date):
			links.append(link[:8])

	for link in links:
		print(link, end=" ")
		en_link = f"https://www.doj.gov.hk/en/community_engagement/sj_blog/{link}_blog1.html"
		zh_link = f"https://www.doj.gov.hk/tc/community_engagement/sj_blog/{link}_blog1.html"

		(en_paragraphs, en_title) = scrape(en_link)
		(zh_paragraphs, zh_title) = scrape(zh_link)

		iso_date = f"{link[0:4]}-{link[4:6]}-{link[6:8]}"

		print(len(en_paragraphs) == len(zh_paragraphs))
		data = {
			"en_url": en_link,
			"zh_url": zh_link,
			"category": "Blog",
			"en_title": en_title,
			"zh_title": zh_title,
			"release_date": iso_date,
			"para_aligned_status": len(en_paragraphs) == len(zh_paragraphs),
			"contents": {
				"en": en_paragraphs,
				"zh": zh_paragraphs
			}
		}

		with open(f"blog_output/{link}.json", "w") as json_file:
			json.dump(data, json_file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
	main()
