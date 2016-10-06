import requests
import bs4
import time
import crawler_helper


def extract_posting(soup):
    posting = {}
    posting['title'] = soup.find('span', {'itemprop': 'name'}).text
    table = soup.find('table', {'class': 'ad-attributes'})
    for row in table.find_all('tr'):
        key = row.find('th')
        value = row.find('td')
        if not key or not value:
            continue
        value = value.text.replace('View map', '')
        posting[key.text.strip()] = ' '.join(value.split())
    images_container = soup.find('ul', {'id': 'ShownImage'})
    images = [image['src'] for image in images_container.find_all('img')]
    posting['images'] = images
    posting['body'] = ' '.join(soup.find('span', {'itemprop': 'description'})
                               .text
                               .split())
    return posting


def crawl_searched_vans(links, car, category):
    crawler_helper.update_deadlinks(vans, links, False)
    links = (link for link in links if link not in vans)
    for url in links:
        van = requests.get(url)
        try:
            posting = extract_posting(bs4.BeautifulSoup(van.text))
        except:
            posting = {}
        posting['url'] = url
        posting['query'] = car
        posting['type'] = category
        posting['date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        posting['deadlink'] = False
        posting['crawler'] = 'Kijji'
        vans[url] = posting
        time.sleep(5)


def crawl_vans():
    category_link = \
        {'van': 'http://www.kijiji.ca/b-cars-trucks/british-columbia/%s/' +
            'mini+van__other+body+type/k0c174l9007a138?price=10__12000',
         'rv': 'http://www.kijiji.ca/b-rv-camper-trailer/british-columbia/%s/' +
            'k0c172l9007?price=10__12000'}
    cars = ['dodge ram van', 'ford tuscany van', 'food truck', 'chevy express',
            'gmc savana', 'ford econoline', 'sprinter', 'nissan nv',
            'ford e350', 'ford transit', 'chevy astro', 'gmc safari', 'cargo van']
    cars = [car.replace(' ', '-') for car in cars]

    for category in category_link:
        for car in cars:
            search_page = category_link[category] % car
            print (search_page)
            response = requests.get(search_page)

            soup = bs4.BeautifulSoup(response.text)
            try:
                links = [tag.find('a')['href'] for tag in
                         soup.find('div', {'class': 'container-results'})
                         .find_all('div', {'class': 'clearfix'})]
                links = ['http://www.kijiji.ca%s' % link for link in links]
                print (len(links))
                time.sleep(3)
                crawl_searched_vans(links, car, category)
            except:
                print (0)
                pass


filename = 'kijjivans.json'
vans = crawler_helper.load_vans(filename)
crawl_vans()
crawler_helper.save_vans(filename, vans)
