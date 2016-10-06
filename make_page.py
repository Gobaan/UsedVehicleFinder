import json
import pandas
import itertools
import hashlib
from string import Template
import requests
import shutil
import time
import os.path
session = requests.Session()


with open('autotradevans.json') as fp, \
     open('kijjivans.json') as fp2, \
     open('craigslistvans.json') as fp3, \
     open('repos.json') as fp4:
    autotrade_vans = [json.loads(line) for line in fp]
    for van in autotrade_vans:
        van['crawler'] = 'autotrade'
    kijji_vans = [json.loads(line) for line in fp2]
    for van in kijji_vans:
        van['crawler'] = 'kijji'
    craigslist_vans = [json.loads(line) for line in fp3]
    for van in craigslist_vans:
        van['crawler'] = 'craigslist'
    vans = autotrade_vans + kijji_vans + craigslist_vans
    repos_vans = [json.loads(line) for line in fp4]
    vans = autotrade_vans + kijji_vans + craigslist_vans + repos_vans
    print (len(vans))


def preprocess_vans(vans):
    for van in vans:
        odometer = '0'
        if 'odometer' in van:
            odometer = str(van['odometer'])

        if 'Kilometres' in van:
            odometer = van['Kilometres']

        if 'Kilometers' in van:
            odometer = van['Kilometers']

        odometer = odometer.replace(',', '').replace('km', '').strip()
        try:
            odometer = float(odometer)
        except Exception as e:
            print (e, odometer)
            odometer = 0.0

        if odometer < 1000:
            odometer = odometer * 1000
        van['odometer'] = odometer

        if 'Price' in van:
            van['price'] = van['Price']

        if 'price' not in van:
            van['price'] = '0'

        if 'query' not in van:
            van['query'] = "Autotrader"

        van['price'] = str(van['price']).replace(',', '').replace('$', '')
        try:
            van['price'] = float(van['price'])
        except:
            van['price'] = 0.0
        try:
            van['city'] = van['city'].lower()
        except:
            van['city'] = ' '.join(van['url'].split('/')[4].split('-')[:-1])


preprocess_vans(vans)
frame = pandas.DataFrame(vans)
frame['value'] = 1 / (frame['price'] * frame['odometer'] * frame['odometer'])
frame = frame.drop_duplicates(subset=['price', 'title', 'odometer'])

canadian_cities = ["vancouver", "abbotsford", "whistler", "kamloops", "kelowna"]
us_cities = ['bellingham', 'seattle']
localonly = (~frame['city'].isin(us_cities)) & \
            (frame['price'] < 12000) & \
            (frame['odometer'] < 200000) & \
            (~frame['deadlink'])

points = frame[localonly]
lookup = {}
next_index = 0
for index, isLocal in zip(itertools.count(), localonly):
    if isLocal:
        lookup[next_index] = index
        next_index += 1

carasol = Template('''
<div id='$name' class='carousel slide' data-ride='carousel'>
    <!-- Indicators -->
    <ol class='carousel-indicators'>
      $labels
    </ol>

    <!-- Wrapper for slides -->
    <div class='carousel-inner' role='listbox'>
      $images
    </div>

    <!-- Left and right controls -->
    <a class='left carousel-control' href='#$name' role='button' data-slide='prev'>
      <span class='glyphicon glyphicon-chevron-left' aria-hidden='true'></span>
      <span class='sr-only'>Previous</span>
    </a>
    <a class='right carousel-control' href='#$name' role='button' data-slide='next'>
      <span class='glyphicon glyphicon-chevron-right' aria-hidden='true'></span>
      <span class='sr-only'>Next</span>
    </a>
  </div>''')
label = Template('''<li data-target='#$name' data-slide-to='$count'></li>''')
image = Template('''<div class='item$active'><img src='$image'></div>''')

with open('aggregate.json', 'w') as fp:
    interesting = ['value', 'title', 'url', 'city', 'price', 'odometer',
                   'images']
    local_frame = frame[localonly].fillna("")
    records = local_frame[interesting].to_dict(orient='records')
pandas.set_option('display.max_columns', None)


def get_image_name(url):
    if url.endswith('/$_35.JPG'):
        return url.split('/')[-2] + ".jpg"
    return url.split('/')[-1]

urls = [url for record in records if type(record['images']) is not float
        for url in record['images']]

for url in urls:
    image_name = "images/%s" % get_image_name(url)
    if (os.path.exists(image_name)):
        continue
    print (url)
    response = requests.get(url, stream=True)
    try:
        with open(image_name, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        time.sleep(1)
    except:
        print ("failed: ", url)
        time.sleep(60)

for record, index in zip(records, itertools.count()):
    images = []
    labels = []
    name = hashlib.sha256(record['url'].encode('utf-8')).hexdigest()
    if type(record['images']) == float:
        record['images'] = '<div></div>'
        continue

    for image_url, index in zip(record['images'], itertools.count()):
        isActive = " active" if not labels else ""
        images += [image.substitute(image="images/%s" %
                                    get_image_name(image_url), active=isActive)]
        labels += [label.substitute(name=name, count=index)]
    images = ' '.join(images)
    labels = ' '.join(labels)
    actions = ["""<a href='#' onclick='hide("%s");return false;'>
               <img border='0' src='images/x.png' width='32' height='32'>
               </a>""" % name]
    # Forest Green -> Followed up, scheduled a meeting
    # Cadet blue -> Far away
    # Burly wood -> Followed up waiting on response
    # DarkRed -> Closed (unselected)
    # White -> Default
    colors = ['ForestGreen', 'DodgerBlue', 'SandyBrown', 'Crimson', 'White']
    actions += ["""<a href='#' onclick='color("%s", "%s");return false;'>
                <img border='0' src='images/%scheck.png' width='32'
                height='32'></a>""" % (name, color, color) for color in colors]
    actions += [
        ("<a target='_blank' href='%s'><img border='0'" % record['url']) +
        "src='images/goto.png' width='32' height='32'></a>"]
    record['actions'] = ''.join(actions)
    record['id'] = name
    record['images'] = carasol.substitute(name=name,
                                          images=images,
                                          labels=labels)
    record['favourite'] = False


with open('carasol.json', 'w') as fp:
    json.dump(records, fp, indent=4)


with open('carasol.json') as fp, open('images/carasol.json', 'w') as fp2:
    for line in fp:
        line = line.replace('NaN', '""')
        line = line.replace('Infinity', "0")
        fp2.write(line)
