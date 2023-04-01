import os
import sys
import json
import re
import requests
import urllib.request, urllib.parse

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(verbose=True)

# url = 'https://api.vimeo.com/users/2931392/videos?direction=asc&per_page=1&sort=date&access_token=xxxxxxx&page=1'

TOKEN = os.getenv('TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')

def get_video_info(url):
  headers = {'Authorization': 'bearer {}'.format(TOKEN)}
  req = urllib.request.Request(url, headers=headers)
  response = urllib.request.urlopen(req)
  content = response.read()
  return json.loads(content.decode('utf-8'))

def get_download_idx(dl_list):
  max_idx = 0
  curr = 0
  size_list = ['240p', '360p', '480p', '540p', 'source', '720p', '1080p']

  for i, dl in enumerate(dl_list):
    size = dl['rendition']
    idx = size_list.index(size)
    if idx >= max_idx:
      max_idx = idx
      curr = i

  return curr

def download(title, link):
  Path('./downloads').mkdir(parents=True, exist_ok=True)
  filename='./downloads/{}.mp4'.format(title)
  res = requests.get(link)
  with open(filename, "wb") as handle:
    for chunk in res.iter_content(chunk_size=1024):
      if chunk:
          handle.write(chunk)

if __name__ == '__main__':
  base_url = 'https://api.vimeo.com'
  params = {
    'direction': 'asc',
    'sort': 'date',
    'per_page': 1,
    'page': sys.argv[1] if len(sys.argv) > 1 else 1
  }

  url = '{}/users/{}/videos'.format(base_url, CLIENT_ID)
  full_url = '{}?{}'.format(url, urllib.parse.urlencode(params))

  while 1:
    info = get_video_info(full_url)
    if not len(info['data']):
      break

    data = info['data'][0]
    page = info['page']
    date_list = re.findall(r'\d{4}.\d{2}.\d{2}', data['name'])
    if not len(date_list):
      created_time = data['created_time'][:10]
      date = created_time.replace('-', '.')
    else:
      date = date_list[0]

    title = '{} - {}'.format(date, data['name'])
    print(page, title)
    dl_list = data['download']
    if not len(dl_list):
      print('can not find files.')
    else:
      dl_idx = get_download_idx(dl_list)
      print('Downloading file({})...'.format(dl_list[dl_idx]['size_short']), end='')
      download(title, dl_list[dl_idx]['link'])
      print('done')

    # break
    if info['paging']['next']:
      full_url = base_url + info['paging']['next']
    else:
      print('completed')
      break
