import requests
from log import logger
from config import *

class NetworkStatusError(Exception):
    pass



def get_response(url: str,  headers: dict, params={}, use_proxy = False):
    max_retry = 3
    for i in range(max_retry + 1):
        try:
            if use_proxy:
                rs = requests.request(
                    "GET",
                    url=url,
                    params=params,
                    headers=headers,
                    timeout=15,
                    proxies=PROXY
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
