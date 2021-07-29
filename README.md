Scrapes press releases from [doj.gov.hk](https://www.doj.gov.hk/en/community_engagement/press/index.html)

## Suggest library:
|Name|Url|
|----|-----|
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
	"category": "if any",
	"release_date": "isoformat 8601",
	// "para_aligned_status": true/false
	// "sentence_aligned_status": ignore/true/false
	"contents": {
		"zh": [
			"zh-para1",
			"zh-para2"
		],
		"en": [
			"en-para1",
			"en-para2"
		]
		"mixed_enzh" : [
			"you can put some confuse sentences here"
		]
	},
	// optional: split the paragraphs into aligned sentences if you can/
	"sentences": {
		"zh": [
			"zh-para1-sent1",
			"zh-para1-sent2",
			"zh-para2-sent1",
		],
		"en": [
			"en-para1-sent1",
			"en-para1-sent2",
			"en-para2-sent1",
		]
	}
}
```

python webite.py --date 2021-07-28

https://www.doj.gov.hk/en/community_engagement/press/index.html