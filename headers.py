import time

cookies_to_str = lambda cookies: "; ".join([str(x) + "=" + str(y) for x, y in cookies.items()])

plain_cookies = lambda sess_id: {
    'overleaf_session2': sess_id,
}

better_cookies = lambda sess_id, gclb: {
    'overleaf_session2': sess_id,
    'GCLB': gclb
}

sock_get_headers = lambda proj_id: {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,ru;q=0.8',
    'dnt': '1',
    'referer': 'https://www.overleaf.com/project/%s' % proj_id,
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    'sec-ch-ua-mobile': '?0',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/100.0.4896.60 Safari/537.36 '
}
create_socket_headers = {
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,ru;q=0.8',
    'cache-control': 'no-cache',
    'Pragma': 'no-cache',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/100.0.4896.60 Safari/537.36 ',
    'Host': 'www.overleaf.com',
    'Origin': 'https://www.overleaf.com',
}

upload_file_headers = lambda proj_id, csrf: {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,ru;q=0.8',
    'dnt': '1',
    'origin': 'https://www.overleaf.com',
    'referer': 'https://www.overleaf.com/project/%s' % proj_id,
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': 'Windows',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/100.0.4896.60 Safari/537.36 ',
    'x-csrf-token': csrf

}
