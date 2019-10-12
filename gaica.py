import json
import os

import bs4
import requests


class GaicaClient:

    def __init__(self):
        sess = requests.Session()
        resp = sess.get('https://ap.gaica.jp/p/login/RW1312010001')
        assert resp.status_code == 200
        soup = bs4.BeautifulSoup(resp.content, 'html.parser')
        nablarch_hidden = soup.find('input', {'name': 'nablarch_hidden'}).attrs['value']
        nablarch_needs_hidden_encryption = soup.find('input', {'name': 'nablarch_needs_hidden_encryption'}).attrs[
            'value']

        payload = {'usrId': os.environ['GAICA_USER'],
                   'password': os.environ['GAICA_PASS'],
                   'nablarch_needs_hidden_encryption': nablarch_needs_hidden_encryption,
                   'nablarch_hidden': nablarch_hidden,
                   'nablarch_submit': 'nablarch_form1_1'}

        resp = sess.post('https://ap.gaica.jp/p/login/RW1312010101', data=payload)
        assert resp.status_code == 200
        soup = bs4.BeautifulSoup(resp.content, 'html.parser')
        assert 'ご利用のご案内' in soup.text

        self.sess = sess
        self.main_page_soup = soup

    def charge(self):

        attrs = [a.attrs['value'] for a in self.main_page_soup.find_all('input', {'name': 'nablarch_hidden'}) if
                 a.attrs['value'] != '']

        payload = {'nablarch_hidden': attrs[-1], 'nablarch_submit': 'nablarch_form2_3'}

        resp = self.sess.post('https://ap.gaica.jp/p/chargeSetting/RW1323000101', data=payload)
        assert resp.status_code == 200
        soup = bs4.BeautifulSoup(resp.content, 'html.parser')
        assert '新生総合口座パワ' in soup.text

        attrs = [a.attrs['value'] for a in soup.find_all('input', {'name': 'nablarch_hidden'}) if
                 a.attrs['value'] != '']

        payload = {'nablarch_hidden': attrs[-1], 'nablarch_submit': 'nablarch_form3_1'}

        resp = self.sess.post('https://ap.gaica.jp/p/charge/RW13D4010101', data=payload)
        assert resp.status_code == 200
        soup = bs4.BeautifulSoup(resp.content, 'html.parser')
        assert 'チャージする通貨の選択とチャージ' in soup.text

        # input money.

        attrs = [a.attrs['value'] for a in soup.find_all('input', {'name': 'nablarch_hidden'}) if
                 a.attrs['value'] != '']

        payload = {'nablarch_hidden': attrs[-1], 'nablarch_submit': 'nablarch_form4_1',
                   'W13D401.ksiCrcCod': '392', 'W13D401.ksiKkgNkg': '10000'}

        resp = self.sess.post('https://ap.gaica.jp/p/charge/RW13D4010201', data=payload)
        assert resp.status_code == 200
        soup = bs4.BeautifulSoup(resp.content, 'html.parser')
        assert '入力内容に誤りがないか' in soup.text

        # https://ap.gaica.jp/p/charge/RW13D4010201
        # nablarch_form4_1
        # W13D401.ksiCrcCod: 392
        # W13D401.ksiKkgNkg: 1000 (amount in yen)
        # <option value="392">JPY</option>
        # <option value="840">USD</option>
        # <option value="978">EUR</option>
        # <option value="826">GBP</option>
        # <option value="036">AUD</option>
        # display_none:

        # click to confirm.
        attrs = [a.attrs['value'] for a in soup.find_all('input', {'name': 'nablarch_hidden'}) if
                 a.attrs['value'] != '']

        payload = {'nablarch_hidden': attrs[3], 'nablarch_submit': 'nablarch_form4_2'}

        resp = self.sess.post('https://ap.gaica.jp/p/charge/RW13D4010301', data=payload)
        assert resp.status_code == 200
        soup = bs4.BeautifulSoup(resp.content, 'html.parser')
        assert 'チャージ手続きが完了しました' in soup.text
        return 'Charged.'

    def fetch_balance(self):

        attrs = [a.attrs['value'] for a in self.main_page_soup.find_all('input', {'name': 'nablarch_hidden'}) if
                 a.attrs['value'] != '']

        payload = {'nablarch_hidden': attrs[-1], 'nablarch_submit': 'nablarch_form2_5'}

        resp = self.sess.post('https://ap.gaica.jp/p/balanceInquiry/RW1314010101', data=payload)
        assert resp.status_code == 200
        soup = bs4.BeautifulSoup(resp.content, 'html.parser')
        assert 'カード残高の確' in soup.text

        attrs = [a.attrs['value'] for a in soup.find_all('input', {'name': 'nablarch_hidden'}) if
                 a.attrs['value'] != '']

        payload = {'nablarch_hidden': attrs[-1], 'nablarch_submit': 'nablarch_form3_1'}

        resp = self.sess.post('https://ap.gaica.jp/p/balanceInquiry/RW1314010201', data=payload)
        assert resp.status_code == 200
        soup = bs4.BeautifulSoup(resp.content, 'html.parser')
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
                    x = [str(t.contents[0]).strip().replace(u'\xa0', u' ') for t in tr_s[j].contents if
                         str(t).strip() != '']
                    spending_type, spending_daily, spending_month = x
                    # print(str(spending_type).ljust(20), str(spending_daily).ljust(20), spending_month)
                    json_result[spending_type] = {'1日': spending_daily, '1ヶ月': spending_month}

        output = json.dumps(json_result, indent=4, ensure_ascii=False)
        print(output)
        return output


if __name__ == '__main__':
    GaicaClient().fetch_balance()
