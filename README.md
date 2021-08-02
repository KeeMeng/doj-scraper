# Scrapes press releases from [doj.gov.hk](https://www.doj.gov.hk/en/community_engagement/press/index.html)

## Suggest library: 
|Name|Url|
|----|---|
|`Requests:`|`https://requests.readthedocs.io/en/master/`|
|`Beautiful Soup:`|`https://www.crummy.com/software/BeautifulSoup/bs4/doc/`|
|`Selenium:`|`https://selenium-python.readthedocs.io/`|
|`scrapy`|`https://scrapy.org/`|


## Output format: 
Should be a json, 1 document per json
```
{
	"en_url": "",
	"zh_url": "",
	"category": "Press Release",
	"en_title": "",
	"zh_title": "",
	"release_date": "yyyy-mm-dd",
	"para_aligned_status": True,
	"sentence_aligned_status": False,
	"contents": {
		"en": [],
		"zh": []
	},
	"sentences": {
		"en": [],
		"zh": [],
		"enzh": [],
		"others": []
	}
}
```

## Usage: 
`python scraper.py --date 2021-08-02`
