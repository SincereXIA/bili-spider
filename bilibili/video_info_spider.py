from bilibili_api import video, Verify
import config
import requests
import re
from fake_useragent import UserAgent
from bilibili.common import get_response


class VideoInfoSpider:
    def __init__(self):
        for i in range(3):
            try:
                self._ua = UserAgent()
            except Exception:
                pass
            else:
                break

    def get_video_info(self, aid):
        #verify = Verify(sessdata=config.SESSDATA, csrf=config.CSRF)
        my_video = video.VideoInfo(aid=aid)
        video_info = my_video.get_video_info()
        video_info['online_count'] = self.get_online_count(bvid=video.aid2bvid(aid), cid=video_info['cid'])
        self.get_total_count(aid)
        return video_info

    def get_cid(self, avid):
        bvid = video.aid2bvid(avid)
        headers = {
            "origin": "https://www.bilibili.com",
            "referer": f"https://www.bilibili.com/video/{bvid}",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "user-agent": self._ua.random,
        }
        rs = get_response(
            url="http://api.bilibili.com/x/player/pagelist",
            headers=headers,
            params={
                'aid': avid
            }
        )
        js = rs.json()
        return js['data'][0]['cid']

    def get_total_count(self, avid):
        bvid = video.aid2bvid(avid)
        headers = {
            "origin": "https://www.bilibili.com",
            "referer": f"https://www.bilibili.com/video/{bvid}",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "user-agent": self._ua.random,
        }
        rs = get_response(
            url="http://api.bilibili.com/archive_stat/stat",
            headers = headers,
            params= {
                'aid': avid
            }
        )
        js = rs.json()
        return js['data']

    def get_online_count_and_tid(self, avid, cid):
        bvid = video.aid2bvid(avid)
        headers = {
            "origin": "https://www.bilibili.com",
            "referer": f"https://www.bilibili.com/video/{bvid}",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "user-agent": self._ua.random,
        }
        aid = video.bvid2aid(bvid)
        rs = get_response(
            url=f"https://api.bilibili.com/x/player.so?id=cid%3A{cid}&aid={aid}",
            headers=headers
        )
        search_obj = re.search("<online_count>([0-9]*)</online_count>", rs.text, )
        online = int(search_obj.group(1))
        search_obj = re.search("<typeid>([0-9]*)</typeid>", rs.text, )
        tid = int(search_obj.group(1))
        return (online, tid)

    def get_online_count(self, bvid: str, cid: int):
        headers = {
            "origin": "https://www.bilibili.com",
            "referer": f"https://www.bilibili.com/video/{bvid}",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "user-agent": self._ua.random,
        }
        aid = video.bvid2aid(bvid)
        rs = get_response(
            url=f"https://api.bilibili.com/x/player.so?id=cid%3A{cid}&aid={aid}",
            headers=headers
        )
        search_obj = re.search("<online_count>([0-9]*)</online_count>", rs.text, )
        return int(search_obj.group(1))
