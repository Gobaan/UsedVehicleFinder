import os.path
import json
import shutil


def update_deadlinks(vans, urls, value):
    for url in urls:
        if url in vans:
            vans[url]['deadlink'] = value


def load_vans(filename):
    if not os.path.exists(filename):
        with open(filename, 'w') as fp:
            pass

    with open(filename, 'r') as fp:
        vans = [json.loads(line) for line in fp]
        vans = {van['url']: van for van in vans}

    update_deadlinks(vans, vans, True)
    return vans


def save_vans(filename, vans):
    if os.path.exists(filename):
        shutil.copyfile(filename, "%s.backup" % filename)

    with open(filename, 'w') as fp:
        for van in vans:
            fp.write('%s\n' % json.dumps(vans[van]))
