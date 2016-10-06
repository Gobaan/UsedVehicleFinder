import time
import bs4
import requests
from time import gmtime, strftime
import crawler_helper


def search_cars(city, car):
    domain = "http://%s.craigslist.ca" % city
    url_base = '%s/search/eby/cta' % domain
    params = {'max_price': 15000, 'max_auto_miles': 400000,
              'auto_bodytype': [12], 'query': [car]}
    try:
        rsp = requests.get(url_base, params=params)
    except Exception as e:
        print ('failed:', url_base, e)
        rsp = DummyResponse()
    return extract_vans(rsp, domain)


def search_rvs(city):
    domain = "http://%s.craigslist.ca" % city
    url_base = '%s/search/eby/rva' % domain
    params = dict(max_price=15000, max_auto_miles=400000, query=["van"])
    try:
        rsp = requests.get(url_base, params=params)
    except Exception as e:
        print ('failed:', url_base, e)
        rsp = DummyResponse()
    return extract_vans(rsp, domain)


def extract_vans(rsp, domain):
    def startsWithRds(x): return x.startswith('/') and x.endswith('.html')
    print ('domain:', domain)
    html = bs4.BeautifulSoup(rsp.text, 'html.parser') \
        .find('div', {'class': 'rows'})
    local = set()
    expanded = set()
    after = False
    children = (child for child in html.children if child.name)
    for child in children:
        after = after or child.name == "h4"
        van = child.find_all('a', href=startsWithRds)
        if not van:
            continue
        site = "%s%s" % (domain, van[0]['href'])
        if after:
            expanded.add(site)
        else:
            local.add(site)

    time.sleep(2)
    return rsp, local, expanded


class DummyResponse(object):
    def __init__(self):
        self.text = "<html><div class='rows'/></html>"


def extract_posting(city, query, posting_urls, expanded=False):
    crawler_helper.update_deadlinks(vans, posting_urls, False)
    posting_urls = [url for url in posting_urls if url not in vans]
    for posting_url in posting_urls:
        print (posting_url)
        response = requests.get(posting_url)
        txt = bs4.BeautifulSoup(response.text, 'html.parser')

        details = txt.find(attrs={'class': 'mapAndAttrs'}).findAll('span')
        details = [detail.text for detail in details]
        details[0] = "model: " + details[0]
        details = [detail.split(":") for detail in details]
        garbage = [detail[0] for detail in details if len(detail) == 1]
        details = {detail[0]: detail[1].strip() for detail in details
                   if len(detail) == 2}

        images = txt.findAll("img")
        images = [image["src"].replace('50x50c', '600x450') for image in images]

        title = txt.find("span", {"id": "titletextonly"}).text
        price = txt.find("span", {"class": "price"}).text

        body = txt.find("section", {"id": "postingbody"})
        details['body'] = str(body)
        details['images'] = images
        details['garbage'] = garbage
        details['title'] = title
        details['price'] = price
        details['query'] = query
        details['city'] = city
        details['url'] = posting_url
        details['expanded'] = expanded
        details['date'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        details['deadlink'] = False
        vans[posting_url] = details
        time.sleep(5)


# Todo: make this less stupid
def extract_postings(cities, cars):
    for city in cities:
        for car in cars:
            try:
                rsp, local, expanded = search_cars(city, car)
                extract_posting(city, car, local, False)
            except:
                pass

        try:
            rsp, local, expanded = search_rvs(city)
            extract_posting(city, "rv", local, False)
        except:
            pass

    for city in cities:
        for car in cars:
            try:
                rsp, local, expanded = search_cars(city, car)
                extract_posting(city, car, expanded, True)
            except:
                pass

        try:
            rsp, local, expanded = search_rvs(city)
            extract_posting(city, "rv", expanded, True)
        except:
            pass

cities = ["vancouver", "bellingham", "comoxvalley", "abbotsford", "kamloops",
          "kelowna", "moseslake", "nanaimo", "olympic", "seattle", "skagit",
          "sunshine", "victoria", "wenatchee", "whistler", "yakima"]
cities += ["calgary", "edmonton", "ftmcmurray", "reddeer"]
cities = ["vancouver", "abbotsford", "whistler", "kamloops", "kelowna"]
cars = ["dodge ram van", "ford tuscany van", "food truck", "chevy express",
        "gmc savana", "ford econoline", "ford e350", "ford transit",
        "cargo van", "nissan nv", 'chevy astro', 'gmc safari', "sprinter", "passenger van"]

filename = 'craigslistvans.json'
vans = crawler_helper.load_vans(filename)
extract_postings(cities, cars)
crawler_helper.save_vans(filename, vans)
