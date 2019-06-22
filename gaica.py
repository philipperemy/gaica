import json
import os

import bs4
import requests

sess = requests.Session()

resp = sess.get('https://ap.gaica.jp/p/login/RW1312010101')
assert resp.status_code == 200
soup = bs4.BeautifulSoup(resp.content, 'lxml')
nablarch_hidden = soup.find('input', {'name': 'nablarch_hidden'}).attrs['value']
nablarch_needs_hidden_encryption = soup.find('input', {'name': 'nablarch_needs_hidden_encryption'}).attrs['value']

payload = {'usrId': os.environ['GAICA_USER'],
           'password': os.environ['GAICA_PASS'],
           'nablarch_needs_hidden_encryption': nablarch_needs_hidden_encryption,
           'nablarch_hidden': nablarch_hidden,
           'nablarch_submit': 'nablarch_form1_1'}

resp = sess.post('https://ap.gaica.jp/p/login/RW1312010101', data=payload)
assert resp.status_code == 200
soup = bs4.BeautifulSoup(resp.content, 'lxml')
assert 'ご利用のご案内' in soup.text

attrs = [a.attrs['value'] for a in soup.find_all('input', {'name': 'nablarch_hidden'}) if a.attrs['value'] != '']

payload = {'nablarch_hidden': attrs[-1], 'nablarch_submit': 'nablarch_form2_5'}

resp = sess.post('https://ap.gaica.jp/p/balanceInquiry/RW1314010101', data=payload)
assert resp.status_code == 200
soup = bs4.BeautifulSoup(resp.content, 'lxml')
assert 'カード残高の確' in soup.text

nablarch_hidden = soup.find('div', {'id': 'header'}).find('input', {'name': 'nablarch_hidden'}).attrs['value']

attrs = [a.attrs['value'] for a in soup.find_all('input', {'name': 'nablarch_hidden'}) if a.attrs['value'] != '']

payload = {'nablarch_hidden': attrs[-1], 'nablarch_submit': 'nablarch_form3_1'}

resp = sess.post('https://ap.gaica.jp/p/balanceInquiry/RW1314010201', data=payload)
assert resp.status_code == 200
soup = bs4.BeautifulSoup(resp.content, 'lxml')
assert '通貨コード' in soup.text

json_result = {}

results = soup.find_all('div', {'class': 'nablarch_listSearchResultWrapper'})
assert len(results) == 2
for i, result in enumerate(results):
    tr_s = result.find_all('tr')
    if i == 0:  # first table.
        headers = [t.contents[0].strip() for t in tr_s[1].contents if str(t).strip() != '']
        data = [t.contents[0].strip() for t in tr_s[2].contents if str(t).strip() != '']
        for h, d in zip(headers, data):
            # print(str(h).ljust(20), d)
            json_result[h] = d
    else:
        for j in range(3, 6):
            x = [str(t.contents[0]).strip().replace(u'\xa0', u' ') for t in tr_s[j].contents if str(t).strip() != '']
            spending_type, spending_daily, spending_month = x
            # print(str(spending_type).ljust(20), str(spending_daily).ljust(20), spending_month)
            json_result[spending_type] = {'1日': spending_daily, '1ヶ月': spending_month}

print(json.dumps(json_result, indent=4, ensure_ascii=False))
