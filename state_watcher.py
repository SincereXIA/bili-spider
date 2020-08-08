from database import DBSession, VideoInfo, VideoState, ZoneInfo
from bilibili import *
from sqlalchemy import exists
import datetime
import time
from log import logger
import threading
from queue import Queue


class Watcher_Thread(threading.Thread):
    task_queue: Queue
    thread_id: int
    use_proxy: bool

    def __init__(self, thread_id: int, task_queue: Queue, use_proxy=False):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.task_queue = task_queue
        self.use_proxy = use_proxy
        self.session = DBSession()
        self.spider = VideoInfoSpider(use_proxy=use_proxy)

    def _watch_video(self, video):
        if not video.cid:
            try:
                video.cid = self.spider.get_cid(video.aid)
            except Exception as e:
                logger.error(f"T:{self.thread_id} 获取 {video.aid} cid出错：\n {e}")
                time.sleep(2)
                return
            video.first_get_state_time = datetime.datetime.now()
        try:
            online_count, zid = self.spider.get_online_count_and_tid(video.aid, video.cid)
        except Exception as e:
            logger.error(f"T:{self.thread_id} 获取 {video.aid} 在线观看人数出错：\n {e}")
            time.sleep(10)
            return
        if not video.zid:
            zone_exists = self.session.query(
                exists().where(ZoneInfo.zid == zid)
            ).scalar()
            if not zone_exists:
                try:
                    new_zone = ZoneInfo(
                        zid=zid,
                    )
                    self.session.add(new_zone)
                    self.session.commit()
                except Exception as e:
                    logger.error(f"写入 {video.aid} zid 出错：\n")
                    self.session.rollback()
                    return
            video.zid = zid
        try:
            total_count = self.spider.get_total_count(video.aid)
        except Exception as e:
            logger.error(f"T: {self.thread_id} 获取 {video.aid} 当前总状态出错：\n{e}")
            time.sleep(10)
            return
        try:
            new_state = VideoState(
                aid=total_count['aid'],
                time=datetime.datetime.now(),
                online=online_count,
                view=total_count['view'],
                danmaku=total_count['danmaku'],
                reply=total_count['reply'],
                favorite=total_count['favorite'],
                coin=total_count['coin'],
                share=total_count['share'],
                like=total_count['like'],
                dislike=total_count['dislike'],
                now_rank=total_count['now_rank'],
                his_rank=total_count['his_rank'],
            )
            self.session.add(new_state)
            video.last_get_state_time = datetime.datetime.now()
            logger.info(f"T:{self.thread_id} {video.aid} {video.title} online: {online_count}, total: {new_state.view}")
            self.session.commit()
        except Exception as e:
            logger.error(f"写入数据库出错\n {e}")
            self.session.rollback()

    def run(self):
        while True:
            if self.task_queue.empty():
                logger.info(f"thread:{self.thread_id} Empty task queue, Done!Done!Done!")
                break
            try:
                video = self.task_queue.get()
                self._watch_video(video)
            except Exception as e:
                logger.error(f"T:{self.thread_id} 爬取任务出错：{e}")



class VideoProducer(threading.Thread):
    videos:list
    task_queue = Queue()

    def __init__(self, videos:list):
        threading.Thread.__init__(self)
        self.videos = videos
        self.videos.reverse()

    def run(self):
        while self.videos:
            if self.task_queue.qsize() < 100:
                logger.info(f"填充队列中，当前队列长度：{self.task_queue.qsize()}, 剩余条目：{len(self.videos)}")
                for i in range(100):
                    self.task_queue.put(self.videos.pop())
                logger.info("队列填充结束")
            logger.info(f"剩余条目：{len(self.videos)}")
            time.sleep(3)



class StateWatcher:
    def startWatchState(self):
        session = DBSession()
        videos = session.query(VideoInfo).order_by(VideoInfo.collect_id).all()
        producer = VideoProducer(videos)
        producer.start()
        watcher_list = []
        for i in range(WATCHER_NUM):
            watcher_list.append(Watcher_Thread(i, task_queue=producer.task_queue, use_proxy=False))

        for i in range(WATCHER_PROXY_NUM):
            watcher_list.append(Watcher_Thread(i+WATCHER_NUM, task_queue=producer.task_queue, use_proxy=True))

        for watcher in watcher_list:
            watcher.start()
        for watcher in watcher_list:
            watcher.join()
        producer.join()



if __name__ == '__main__':
    watcher = StateWatcher()
    watcher.startWatchState()
