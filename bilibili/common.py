import requests
from log import logger

class NetworkStatusError(Exception):
    pass

#proxies = { "http": "http://127.0.0.1:8889", "https": "http://127.0.0.1:8889", }
proxies = {}

def get_response(url: str,  headers: dict, params={}):
    max_retry = 3
    for i in range(max_retry + 1):
        try:
            if proxies:
                rs = requests.request(
                    "GET",
                    url=url,
                    params=params,
                    headers=headers,
                    timeout=4,
                    proxies=proxies
                )
            else:
                rs = requests.request(
                    "GET",
                    url=url,
                    params=params,
                    headers=headers,
                    timeout=4,
                )
        except Exception:
            logger.warn(f"url:{url}, 第 {i} 次请求失败，正在重试")
        else:
            if rs.status_code < 200 or rs.status_code > 400:
                logger.error(f"url:{url}, 请求返回值异常")
                raise NetworkStatusError
            else:
                return rs
    logger.error(f"url: {url}, 多次请求失败")
    raise NetworkStatusError
