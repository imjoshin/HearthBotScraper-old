import time, datetime, praw, re
import settings, auth
from database import Database

def main():
	while True:
		db = Database()
		client = get_client()
		new_threads = get_new_threads(db, client)
		new_cards = get_cards_from_threads(new_threads)
		add_cards_to_db(db, new_cards)
		db.close()
		client = None

		log("Sleeping for %d seconds..." % (settings.SLEEP_TIME), write=False)
		time.sleep(settings.SLEEP_TIME)

def get_client():
	return praw.Reddit(client_id=auth.REDDIT_CLIENT, client_secret=auth.REDDIT_SECRET, user_agent="Hearthscrape")

def get_new_threads(db, client):
	subreddit = client.subreddit(settings.RELEASE_SUB)
	new_threads = []
	for submission in subreddit.new():
		if "Pre-Release Card Discussion" in submission.title:
			card_name = filter_text(submission.title.replace(settings.CARD_PREFIX, "")).strip()
			db.query("SELECT * FROM card WHERE name = '%s'" % (card_name))
			db_cards = db.fetch()

			if True or len(db_cards) == 0:
				new_threads.append(submission)

	return new_threads

def get_cards_from_threads(threads):
	cards = []
	for thread in threads:
		card_info = thread.selftext
		card = {
			'name': filter_text(thread.title.replace(settings.CARD_PREFIX, "")).strip(),
			'cost': get_regex_match(card_info, "\*\*Mana Cost\*\*: ([0-9])") or '0',
			'attack': get_regex_match(card_info, "\*\*Attack\*\*: ([0-9])") or 'null',
			'health': get_regex_match(card_info, "\*\*Health\*\*: ([0-9])") or get_regex_match(card_info, "\*\*Durability\*\*: ([0-9])") or 'null',
			'class': get_regex_match(card_info, "\*\*Class\*\*: ([a-zA-Z]+)") or 'Neutral',
			'type': get_regex_match(card_info, "\*\*Type\*\*: ([a-zA-Z]+)") or 'Minion',
			'rarity': get_regex_match(card_info, "\*\*Rarity\*\*: ([a-zA-Z]+)") or 'Minion',
			'text': filter_text(get_regex_match(card_info, "\*\*Text\*\*: (.*)")) or '',
			'set': settings.EXPANSION_NAME,
			'expiration': settings.EXPANSION_RELEASE,
			'image': get_regex_match(card_info, "\[Card Image\]\((.*)\)") or '',
		}

		card['text'] = card['text'].replace("**", "")
		card['image'] = card['image'].replace("imgur", "i.imgur") + ".png"

		log("Found {}".format(card['name']))

		cards.append(card)

	return cards

def add_cards_to_db(db, cards):
	for card in cards:
		query =  """
		INSERT INTO card (name, `set`, class, type, text, rarity, cost, attack, health, img, expiration, collectible, added_by)
		VALUES ("%s", "%s", "%s", "%s", "%s", "%s", %s, %s, %s, "%s", "%s", 1, -1)
		""" % (card['name'], card['set'], card['class'], card['type'], card['text'], card['rarity'], card['cost'], card['attack'], card['health'], card['image'], card['expiration'])

		db.query(query)
		log("Added {}".format(card['name']))

def get_regex_match(subject, regex_str, match_num=1):
	regex = re.compile(regex_str)
	match = regex.search(subject)
	return match.group(match_num) if match else None

def filter_text(str):
	str = ' '.join(str.split())
	str = str.replace("'", "\\'")
	return str

def log(str, write=True):
	logFile = "log"
	p = "%s : %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), str)
	print(p)
	if write:
		with open(logFile, "a") as l:
			l.write("%s\n" % p)

if __name__ == "__main__":
	main()
