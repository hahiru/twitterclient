import os
import sys
import cv2
import yaml
import json
from requests_oauthlib import OAuth1Session
from typing import Optional
import urllib

BASE_URL = "https://api.twitter.com/"


class TwitterClient:
    __slots__ = ['_client', '_func']

    def __init__(self, func) -> None:
        '''
        :param func: 取得したデータに対して処理したい関数を指定します。
        '''
        config = self._load_yaml('config/api.yml')
        self._client = OAuth1Session(
            config['CONSUMER_KEY'], config['CONSUMER_SECRET'], config['ACCESS_TOKEN'], config['ACCESS_TOKEN_SECRET'])
        self._func = func

    def get_timeline(self, count: Optional[int] = 5) -> None:
        '''
        自身のタイムラインを取得します。

        :param count: 取得数
        '''
        params = {'count': count}
        url = os.path.join(BASE_URL, '1.1/statuses/user_timeline.json')
        res = self._client.get(url, params=params)

        self._response_processor(res)

    def get_user_timeline(self, screen_name: str, count: Optional[int] = 5) -> None:
        '''
        特定ユーザのタイムラインを取得します。

        :param screen_name: 特定ユーザのスクリーンネーム
        :param count: 取得数
        '''
        params = {'screen_name': screen_name, 'count': count}
        url = os.path.join(BASE_URL, '1.1/statuses/user_timeline.json')
        res = self._client.get(url, params=params)

        self._response_processor(res)

    def get_user_list(self, screen_name: str) -> None:
        '''
        特定のユーザのリストを取得します。
        '''
        params = {'screen_name': screen_name}
        url = os.path.join(BASE_URL, '1.1/lists/memberships.json')
        res = self._client.get(url, params=params)

        self._response_processor(res)

    def search(self, screen_name: str, count: Optional[int] = 5, until: Optional[str] = None) -> None:
        query = 'from:' + screen_name + ' until:' + until
        query = urllib.parse.quote(query)
        print(query)
        params = {'q': query, 'count': count, 'result_type': 'mixed'}
        url = os.path.join(BASE_URL, '1.1/search/tweets.json')
        res = self._client.get(url, params=params)

        self._response_processor(res)

    def _response_processor(self, res) -> None:
        if res.status_code == 200:
            result = json.loads(res.text)
            self._func(result)
        else:
            print("Failed: %d" % res.status_code)

    def _load_yaml(self, path: str):
        f = open(path, 'r+')
        data = yaml.load(f)
        return data


if __name__=='__main__':
    '''
    config/api.yml にコンシューマーキーを記載してください

    excution)
    python -m twitterclient hinata_980115
    '''
    def display_timeline(timelines):
        for line in timelines:
            print(('::').join([line['user']['name'], line['text'], line['created_at']]))
            print('*******************************************')

    def take_images(timelines, dir_name='images/twitter/'):
        for line in timelines:
            screen_name = line['user']['screen_name']
            save_dir = os.path.join(dir_name, screen_name)
            if not os.path.exists(save_dir):
                os.mkdir(save_dir)
            if line.get('extended_entities'):
                for media in line['extended_entities']['media']:
                    print(media['media_url'])
                    image_url = media['media_url']
                    with open(os.path.join(save_dir, os.path.basename(image_url)), 'wb') as f:
                        img = urllib.request.urlopen(image_url).read()
                        f.write(img)

    def display_lists(lists):
        print('count: ', len(lists['lists']))
        for item in lists['lists']:
            print(item['name'])

    def search_parser(response):
        for item in response['statuses']:
            print('created_at: ', item['created_at'])
            print('text: ', item['text'])
            print('name: {}, screenname: {}'.format(item['user']['name'], item['user']['screen_name']))

    args = sys.argv

    twitter_client = TwitterClient(search_parser)

    # 実行したい動作以外をコメントアウト。要修正
    # twitter_client.get_timeline(take_images)
    # twitter_client.get_user_timeline(args[1], count=100)
    # twitter_client.get_user_list(args[1])
    twitter_client.search(args[1])
