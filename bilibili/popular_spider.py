import requests
import logging
from bilibili.common import get_response
from log import logger
from config import  *
logging.getLogger().setLevel(logging.INFO)

class PopularSpider:
    headers = {
        "origin": "https://www.bilibili.com",
        "referer": f"https://www.bilibili.com/v/channel?spm_id_from={SPM_ID}",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
    }

    def get_channel_list(self, offset=0, list_id=100):
        url = "https://api.bilibili.com/x/web-interface/web/channel/category/channel_arc/list"
        params = {
            "id": list_id,
            "offset": offset,
        }
        rs = get_response(url=url,
                          params=params,
                          headers=self.headers)
        js = rs.json()
        has_more, offset, result = js['data']['has_more'], js['data']['offset'], js['data']['archive_channels']
        return (has_more, offset, result)

    def get_all_channels(self, limit=999999999):
        has_more = True
        offset = 0
        result = []
        logging.info("开始获取所有频道")
        try:
            while has_more and len(result) < limit:
                has_more, offset, r = self.get_channel_list(offset, list_id=0)
                result.extend(r)
                logging.info(f"当前频道总数{len(result)}")
                print(len(result))
        except Exception:
            print("ERROR!!!", f" offset: {offset}")
        logging.info("所有频道获取完毕")
        return result

    def get_all_popular_channels(self):
        has_more = True
        offset = 0
        result = []
        while has_more:
            has_more, offset, r = self.get_channel_list(offset)
            result.extend(r)
        return result

    def _get_channel_hot_video(self, channel_id: int, offset: str = ""):
        page_size = 30
        sort_type = "hot"
        url = "https://api.bilibili.com/x/web-interface/web/channel/multiple/list"
        params = {
            "channel_id": channel_id,
            "sort_type": sort_type,
            "page_size": page_size,
        }
        if offset:
            params['offset'] = offset
        rs = get_response(url=url,
                          params=params,
                          headers=self.headers)
        js = rs.json()
        has_more = js['data']['offset']
        next_offset = js['data']['offset']
        result = []
        if not offset:
            for l in js['data']['list']:
                if 'items' in l.keys():
                    result.extend(l['items'])
                else:
                    result.append(l)
        else:
            result = js['data']['list']
        return (has_more, next_offset, result)

    def get_channel_hot_video(self, channel_id: int, video_num: int) -> list:
        rs = []
        offset = ""
        has_more = True
        while (len(rs) < video_num and has_more):
            has_more, offset, r = self._get_channel_hot_video(channel_id, offset)
            rs.extend(r)
            print(f"channel: {channel_id}, videoNum: {len(rs)}")
        return rs


if __name__ == '__main__':
    spider = PopularSpider()
    # spider.get_all_channels()
    # spider.get_all_popular_channels()
    # spider.get_channel_list()
    spider.get_channel_hot_video(1833, 100)
