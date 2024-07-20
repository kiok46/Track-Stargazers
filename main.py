import os
import urllib.request
import requests
from bs4 import BeautifulSoup
import json
import threading
from geopy.geocoders import Nominatim
import time
from dotenv import load_dotenv

class StarThread(threading.Thread):
    """
    Start a new thread to collect the data from either the 
    scraper or the API.
    """
    def __init__(self, threadID, name, stargazers, data_file, use_api):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.stargazers = stargazers
        self.data_file = data_file
        self.use_api = use_api

    def run(self):
        print("Starting " + self.name)
        store_in_json(self.stargazers, self.data_file, self.use_api)
        print("Exiting " + self.name)


def scrape_stargazers(url):
    """
    Scrape the stargazers page of requested repo.
    
    e.g: http://github.com/kivy/plyer/stargazers?page=1
         http://github.com/kivy/plyer/stargazers?page=2

    returns the entire valid users list.

    """
    page_count = 1
    stargazers = []
    
    while 0 < page_count < 101:
        url_ = url.format(page_count)
        r = urllib.request.urlopen(url_).read()
        soup = BeautifulSoup(r, "lxml")
        # follow = soup.find_all("h2", class_="h4 mb-1")
        follow = [a.text for a in soup.find_all('a', {'data-hovercard-type': 'user'}) if a.text.strip()]
        if follow:
            for human in follow:
                # h = human.a['href'].split("/")[1]
                stargazers.append(human)
            page_count += 1
        else:
            page_count = -1
    time.sleep(0.1)
    return stargazers


# Get user data from API.

def get_user_profile(user_name):
    """
    Use the GitHub's user API to get the user location and id.
    """
    url_ = "https://api.github.com/users/{}".format(user_name)
    headers = {
        'Authorization': f'token {github_api}',
        'Accept': 'application/vnd.github.v3+json',
    }
    r = requests.get(url_, headers=headers)
    result = r.json()
    return result['location'], result['login']


# Scraper for user Profile.

def get_user_id(soup):
    """
    Returns the user id via the scraper.
    """
    follow = soup.find("meta", {"name": "octolytics-dimension-user_id"})["content"]
    return int(follow)


def get_user_country(soup):
    """
    Returns the location of the user via the scraper.
    """
    follow = soup.find("li", itemprop="homeLocation")
    if not follow:
        country = "N/A"
    else:
        country = (follow.get_text())
    
    return str((country.strip()))


def scrape_profile(url):
    """
    Scrape the user's profile to get user location and id.
    """
    r = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(r, "lxml")
    user_country = get_user_country(soup)
    user_id = get_user_id(soup)
    return user_country, user_id


def chunk_stargazers(seq, num):
    """
    Divide the huge User set into smaller lists.
    
    l = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    print (chunk_stargazers(l, 3))
    print (chunk_stargazers(l, 2))

    output:

    [[1, 2, 3], [4, 5, 6], [7, 8, 9, 10]]
    [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]]
    """
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out


def store_in_json(stargazers, data_file, use_api):
    """
    Store the user data in a json file in folder jsons/.

    eg: jsons/data_1.json
    """
    geolocator = Nominatim(user_agent="geoapiExercises")

    def get_country_by_location(location):
        try:
            location = geolocator.geocode(location, language='en')
            return location.address.split(",")[-1].strip()
        except:
            return "Location not found"

    for user in stargazers:
        if use_api:
            user_location, user_id = get_user_profile(user)
        else:
            url = "https://github.com/{}".format(user)
            user_location, user_id = scrape_profile(url)

        if user_location is None:
            # If no information is available about the user
            # location, just ignore it.
            pass
        else:
            user_country = get_country_by_location(user_location)
            if user_country:
                # user_country, user_id = get_user_profile(url)

                # if location name has typos, the country won't be identified,
                # so imho it's a good idea to keep the location in json
                # for a possible manual check
                user_ = {"user": user_id,
                         "country": user_country,
                         "location": user_location}

                try:
                    outfile = open('jsons/{}.json'.format(data_file), 'r')
                    data = json.load(outfile)
                    outfile.close()
                    data["users"].append(user_)

                    with open('jsons/{}.json'.format(data_file), 'w') as outfile:
                        json.dump(data, outfile, indent=4)

                    print(f"Added user {user} from {user_country}")

                    outfile.close()
                except:
                    users = []
                    users.append(user_)

                    map_data = {"users": users}

                    with open('jsons/{}.json'.format(data_file), 'w') as outfile:
                        json.dump(map_data, outfile, indent=4)

                    outfile.close()

    # map_data = {"users": users}

    print("Part 2/2 complete.")
    print("Done. Check the data.json file.")

    # with open('jsons/{}.json'.format(data_file), 'w') as outfile:
    #    json.dump(map_data, outfile, indent=4)

    # outfile.close()


if __name__ == "__main__":

    """
    python3 main.py https://github.com/kivy/plyer 10 10

    url = https://github.com/kivy/plyer
    Number of chunks of the entire user set = 10
    Number of threads working on I/O and requests = 10
    user api or scraper = 1

    If use api is set to 1 then it will use GitHub's official API
    to get the user data, else it will use the scraper.
    """
    load_dotenv()
    github_api = os.getenv('GITHUB_API_KEY')
    # url = str(sys.argv[1])
    url = 'https://github.com/facebookresearch/faiss'
    number_of_threads = 1
    use_api = 1
    read_from_stargazer_json = 0

    star = "/stargazers?page={}"

    if read_from_stargazer_json:
        with open("users_with_location_not_found.json", "r") as stargazers_file:
            stargazers = json.load(stargazers_file)
        stargazers_file.close()
    
    else:
        print("Collecting users ...")
        stargazers = scrape_stargazers(url+star)
        with open('stargazers.json', 'w') as outfile:
            json.dump(stargazers, outfile, indent=4)
        outfile.close()

    chunked_data = chunk_stargazers(stargazers, number_of_threads)
    if chunked_data:
        print("Made {} chunks of entire user set.".format(number_of_threads))
        print("Part 1/2 complete.")
        print("Working on collecting user data ....")

    thread_list = {}
    print("Creating {} threads ...".format(number_of_threads))
    # threading have no sense when the unauthorized limit of github requests
    # is 10 per hour. Dunno if it works with auth token
    store_in_json(stargazers, 'data_0', use_api)
    # for i in range(number_of_threads, 1):
    #     thread_list["thread{}".format(i)] = StarThread(i, "Thread-{}".format(i),
    #                                                    chunked_data[i], "data_{}".format(i),
    #                                                    use_api)
    #     thread_list["thread{}".format(i)].start()
    #
    # for i in range(number_of_threads, 1):
    #     thread_list["thread{}".format(i)].join()
