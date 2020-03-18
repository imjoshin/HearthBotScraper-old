# coding: utf-8 

import time, datetime
#import urllib2
import urllib.request as urllib2
import settings
from database import Database
from bs4 import BeautifulSoup
import requests

def main():
	while True:
		scan()
		log("Sleeping for %d seconds..." % (settings.SLEEP_TIME), False)
		time.sleep(settings.SLEEP_TIME)

def scan():
	db = Database()

	list_url = settings.BASE_URL
	#list_page = urllib2.urlopen(list_url)
	list_page = requests.get(list_url).text
	list_soup = BeautifulSoup(list_page, 'html.parser')
	cards = list_soup.find_all('tr')
	log("Found %d cards at %s" % (len(cards), list_url))

	# loop through cards
	for card_soup in cards:
		card_link = card_soup.find('a')
		if not card_link:
			continue

		cname = filterText(card_link.text)
		if cname == "Breath of the Infinite":
			continue

		db.query("SELECT * FROM card WHERE name = '%s' AND rtime IS NULL" % (cname))
		db_cards = db.fetch()

		# check if card needs to be parsed
		if len(db_cards) is 0:
			log("Found '%s'" % cname)
			tds = card_soup.find_all('td')
			name_td = tds[0]
			class_td = tds[1]
			rarity_td = tds[2]
			type_td = tds[3]
			cost_td = tds[4]
			attack_td = tds[5]
			health_td = tds[6]
			durability_td = tds[7] if len(tds) > 7 else None

			cset = settings.EXPANSION_NAME
			cexpiration = settings.EXPANSION_RELEASE
			cimg = card_link.attrs['data-tooltip-img']
			ctext = filterText(name_td.find('small').text).replace("’", "'").replace("'", "\'")
			cclass = filterText(class_td.text)
			crarity = filterText(rarity_td.text)
			ctype = filterText(type_td.text)
			ccost = filterText(cost_td.text)
			cattack = filterText(attack_td.text or '')
			chealth = filterText(health_td.text or (durability_td.text if durability_td else ''))

			query =  """
			INSERT INTO card (name, `set`, class, type, text, rarity, cost, attack, health, img, collectible, expiration, added_by)
			VALUES ('%s', '%s', '%s', '%s', '%s', '%s', %d, %s, %s, '%s', %d, '%s', %d)
			""" % (cname, cset, cclass, ctype, ctext, crarity, int(ccost), getNumeric(cattack), getNumeric(chealth), cimg, 1, cexpiration, -1)

			#print(query)
			db.query(query)

def filterText(str):
	if str:
		str = ' '.join(str.split())
		str = str.replace("'", "\\'")
	return str

def getNumeric(i):
    try:
        i = int(i)
        return i
    except ValueError:
        return 'null'

def log(str, write = True):
	logFile = "log"
	p = "%s : %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), str)
	print(p)
	if write:
		with open(logFile, "a") as l:
			l.write("%s\n" % p)

if __name__ == "__main__":
	main()
