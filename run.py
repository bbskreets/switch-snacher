import concurrent.futures
import json
import time
import webbrowser

import simpleaudio as sa
from colorama import Fore

from website import Website

MAX_PRICE = 400


# add new websites
# website types: amazon, bestbuy, source
# Website('https://www.amazon.ca/gp/offer-listing/B07VGRJDFY', 'amazon').save()


def check_site(website):  # threading helper function
    website.check()

    return website


sites = []
with open('sites.json', 'r') as fh:  # loads all sites from json file
    data = json.loads(fh.read())
    for url in data:
        sites.append(Website(url, data[url]))

while True:
    pause = False
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(sites)) as executor:
        results = [executor.submit(check_site, website) for website in sites]

        for f in concurrent.futures.as_completed(results):
            website = f.result()

            if website.valid:
                print(Fore.GREEN + str(website) + Fore.RESET)
                wave_obj = sa.WaveObject.from_wave_file("alert.wav").play()
                webbrowser.open(website.url, new=2)

                pause = True
                input('Press enter to continue checking.')
                pause = False

            else:
                print(Fore.RED + str(website) + Fore.RESET)

    while pause:
        time.sleep(1)

    time.sleep(4)
