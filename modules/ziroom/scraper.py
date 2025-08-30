import os, re
import requests
from bs4 import BeautifulSoup


def query(uri, keyword):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}
    res = requests.get(uri, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    houses = soup.find_all('h5', attrs={'class': 'title sign'})
    return res, [h for h in houses if keyword in h.string],


res, houses = query(os.environ.get('URI'), os.environ.get('KEYWORD'))
if res.status_code == 200:
    fout = open('data.html', 'w')
    fout.write(re.sub(r'\?query_session_id=(\d+)', '', "%s" %  houses))
    fout.close()
