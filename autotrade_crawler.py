import bs4
import requests
import dryscrape
import re
import time
import crawler_helper


def extract_posting(soup):
    posting = {}
    image_container = soup.find('div', {'class': 'flashcontainer'}).text
    image_re = re.compile('<img>(.*?)</img>')
    images = [image for image in image_re.findall(image_container) if image]
    [s.extract() for s in soup('script')]

    for row in soup.find('div', {'class': 'at_specsBox'}) \
            .find_all('div', {'class': 'at_row'}):
        key = row.find('span').text.strip()
        value = row.find('div', {'class': 'at_value'}).text.strip()
        posting[key] = value

    body = soup.find('span', {'class': 'vehicleDescription'}).text.strip()
    title_id = 'ctl00_ctl00_MainContent_MainContent_rptAdDetail' + \
               '_ctl00_adDetailControl_h1Title'
    title = soup.find('h1', {'id': title_id}).text
    title = title.split()
    car, city, price = ' '.join(title[:-3]), title[-2], title[-1]
    price = price.replace(',', '').replace("$", '')

    posting['body'] = body
    posting['car'] = car
    posting['city'] = city
    posting['images'] = images
    posting['price'] = price
    posting['deadlink'] = False
    return (posting)

filename = 'autotradevans.json'
vans = crawler_helper.load_vans(filename)
root = 'http://wwwa.autotrader.ca/heavy-trucks/commercial/bc/?prx=-2&' + \
       'prv=British+Columbia&loc=surrey%2c+bc&sts=New-Used&pRng=10%2c14000&' + \
       'hprc=False&wcp=False&inMarket=advancedSearch&rcs=0&rcp=100'

# sess = dryscrape.Session()
# sess.set_attribute('auto_load_images', False)
# sess.visit(root)
# time.sleep(9)
# soup = bs4.BeautifulSoup(sess.body())
with open('autotrade_home.html') as fp:
    body = ''.join(fp.readlines())
    print ("warning loading old body")
soup = bs4.BeautifulSoup(body)
print (len([s.extract() for s in soup('script')]))

for listing in soup.find_all('div', {'class': 'at_result'}):
    link = listing.find('div', {'class': 'at_infoArea'}).find('a')
    url = link['href']

    if url in vans:
        print ('old link', url)
        vans[url]['deadlink'] = False
        continue
    print (url)
    van = requests.get(url)
    posting = extract_posting(bs4.BeautifulSoup(van.text))
    posting['url'] = url
    vans[url] = posting
    time.sleep(5)

crawler_helper.save_vans(filename, vans)
