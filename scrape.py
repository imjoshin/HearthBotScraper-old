import urllib2, time, datetime
import settings
from database import Database
from bs4 import BeautifulSoup

def main():
	while True:
		scan()
		log("Sleeping for %d seconds..." % (settings.SLEEP_TIME), False)
		time.sleep(settings.SLEEP_TIME)

def scan():
	db = Database()

	# get list of cards for main page
	list_url = "%s/set/%s" % (settings.BASE_URL, settings.EXPANSION)
	list_page = urllib2.urlopen(list_url)
	list_soup = BeautifulSoup(list_page, 'html.parser')
	cards = list_soup.find_all('div', attrs={'class': 'card'})

	# loop through cards
	for card in cards:
		img = card.find('a')
		card_url = "%s%s" % (settings.BASE_URL, img.get('href'))
		card_page = urllib2.urlopen(card_url)
		card_soup = BeautifulSoup(card_page, 'html.parser')

		# get name
		name_span = card_soup.find('h1', attrs={'class': 'cardname'})
		cname = filterText(name_span.find('span').text)

		db.query("SELECT * FROM card WHERE name = '%s' AND rtime IS NULL" % (cname))
		db_cards = db.fetch()

		# check if card needs to be parsed
		if len(db_cards) is 0:
			log("Found '%s'" % cname)

			details_div = card_soup.find('div', attrs={'class': 'icR'})
			details = details_div.find_all('div', attrs={'class': 'tr'})
			img_el = img.find('img')

			if img_el is None:
				continue

			fields = {}

			for detail in details:
				dt = detail.find('dt')
				dd = detail.find('dd')

				if dt is None or dd is None:
					continue

				key = detail.find('dt').text.lower()
				value = detail.find('dd').text
				fields[key] = value
				log("\t%s: %s" % (key, filterText(value)))

			cclass = 'Neutral' if 'class' not in fields else fields['class']
			ctype = '' if 'type' not in fields else fields['type']
			ctext = '' if 'text' not in fields else filterText(fields['text'])
			crarity = '' if 'rarity' not in fields else fields['rarity']
			ccost = '' if 'cost' not in fields else fields['cost']
			cattack = '' if 'attack' not in fields else fields['attack']
			chealth = '' if 'health' not in fields else fields['health']
			cset = settings.EXPANSION_NAME
			cexpiration = settings.EXPANSION_RELEASE
			cimg = "%s%s" % (settings.BASE_URL, img_el.get('src'))

			query =  """
			INSERT INTO card (name, `set`, class, type, text, rarity, cost, attack, health, img, collectible, expiration, added_by)
			VALUES ('%s', '%s', '%s', '%s', '%s', '%s', %d, %d, %d, '%s', %d, '%s', %d)
			""" % (cname, cset, cclass, ctype, ctext, crarity, int(ccost), int(cattack), int(chealth), cimg, 1, cexpiration, -1)

			db.query(query)

def filterText(str):
	str = ' '.join(str.split())
	str = str.replace("'", "\\'")
	return str

def log(str, write = True):
	logFile = "log"
	p = "%s : %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), str)
	print(p)
	if write:
		with open(logFile, "a") as l:
			l.write("%s\n" % p)

if __name__ == "__main__":
	main()
