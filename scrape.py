import urllib2
import settings
from bs4 import BeautifulSoup

def main():
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

        # check if card needs to be parsed
        if True:
            # get name
            name_span = card_soup.find('h1', attrs={'class': 'cardname'})
            cname = name_span.find('span').text
            print cname

            details_div = card_soup.find('div', attrs={'class': 'icR'})
            details = details_div.find_all('div', attrs={'class': 'tr'})
            fields = {}

            for detail in details:
                dt = detail.find('dt')
                dd = detail.find('dd')

                if dt is None or dd is None:
                    continue

                key = detail.find('dt').text.lower()
                value = detail.find('dd').text
                fields[key] = value
                print "\t%s: %s" % (key, ' '.join(value.split()))

            cclass = 'Neutral' if 'class' not in fields else fields['class']
            ctype = fields['type']
            ctext = fields['text']
            crarity = fields['rarity']
            ccost = fields['cost']
            cset = settings.EXPANSION_NAME
            cimg = "%s%s" % (settings.BASE_URL, img.find('img').get('src'))





if __name__ == "__main__":
	main()
