import requests
import bs4
import time
import crawler_helper


roots = ['http://www.repo.com/browse/domestic_cargo_vans_cube_vans/?sort=date-',
         'http://www.repo.com/browse/import_cargo_vans_cube_vans/?sort=date-']

responses = [requests.get(root) for root in roots]
soups = [bs4.BeautifulSoup(response.text) for response in responses]


def startsWithListing(x):
    return x and x.startswith('/listing')


def startsWithAsset(x):
    return x and x.startswith('/assets')


postings = [tag['href'] for soup in soups
            for tag in soup.find_all('a', href=startsWithListing)]
urls = ['http://www.repo.com' + posting for posting in postings]
vans = crawler_helper.load_vans('repos.json')
crawler_helper.update_deadlinks(vans, urls, False)
urls = set([url for url in urls if url not in vans])

postings = {url: requests.get(url) for url in urls}


def extract_posting(van_soup):
    column = van_soup.find('div', {'class': 'col-md-6'})
    table = van_soup.find('table', {'class': 'details table table-striped'})
    posting = {}
    try:
        posting = {key.text[:-1]: ' '.join(value.text.split())
                   for key, value in zip(table.find_all('th'),
                                         table.find_all('td'))}
        posting['images'] = ['http://www.repo.com%s' % tag['src']
                             for tag in van_soup.find_all('img',
                                                          src=startsWithAsset)]
        posting['images'] = posting['images'][1:]
        posting['title'] = column.find('h3').text
        posting['price'] = column.find('h4')\
            .text\
            .split('or')[0]\
            .strip()[1:]\
            .replace(',', '')\
            .replace('.00', '')
        posting['odometer'] = posting['Mileage'].split(' km')[0]
        posting['body'] = column.find('p', {'class': 'summary'}).text.strip()
        posting['city'] = (van_soup
                           .find_all('div', {'class': 'panel-body'})[2]
                           .find_all('div', {'class': 'col-md-6'})[2]
                           .find('p')
                           .text
                           .split('\n')[1].split()[-1])
    except Exception as e:
        print ("Error occured:", e)

    return posting


def crawl_vans(postings):
    for url in postings:
        print (url)
        soup = bs4.BeautifulSoup(postings[url].text)
        posting = extract_posting(soup)
        posting['url'] = url
        posting['date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        posting['deadlink'] = False
        posting['crawler'] = 'Repos'
        vans[url] = posting


filename = 'repos.json'
vans = crawler_helper.load_vans(filename)
crawl_vans(postings)
crawler_helper.save_vans(filename, vans)
