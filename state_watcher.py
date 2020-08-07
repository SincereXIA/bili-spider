from database import DBSession, VideoInfo, VideoState, ZoneInfo
from bilibili import  *
from sqlalchemy import exists
import datetime
import time
from log import logger

class StateWatcher:
    def startWatchState(self):
        spider = VideoInfoSpider()
        session = DBSession()
        videos = session.query(VideoInfo).order_by(VideoInfo.collect_id).all()
        i = 0
        for video in videos:
            i+=1
            print(f"{i}/{len(videos)}")
            if not video.cid:
                try:
                    video.cid = spider.get_cid(video.aid)
                except Exception as e:
                    logger.error(f"获取 {video.aid} cid出错：\n", e)
                    time.sleep(2)
                    continue
                video.first_get_state_time = datetime.datetime.now()
            try:
                online_count, zid = spider.get_online_count_and_tid(video.aid, video.cid)
            except Exception as e:
                logger.error(f"获取 {video.aid} 在线观看人数出错：\n", e)
                time.sleep(2)
                continue
            if not video.zid:
                zone_exists = session.query(
                    exists().where(ZoneInfo.zid == zid)
                ).scalar()
                if not zone_exists:
                    try:
                        new_zone = ZoneInfo(
                            zid=zid,
                        )
                        session.add(new_zone)
                        session.commit()
                    except Exception:
                        logger.error(f"写入 {video.aid} zid 出错：\n", e)
                        session.rollback()
                        continue
                video.zid = zid
            try:
                total_count = spider.get_total_count(video.aid)
            except Exception as e:
                logger.error(f"获取 {video.aid} 当前总状态出错：\n", e)
                continue
            try:
                new_state = VideoState(
                    aid=total_count['aid'],
                    time=datetime.datetime.now(),
                    online=online_count,
                    view = total_count['view'],
                    danmaku=total_count['danmaku'],
                    reply = total_count['reply'],
                    favorite=total_count['favorite'],
                    coin=total_count['coin'],
                    share=total_count['share'],
                    like=total_count['like'],
                    dislike=total_count['dislike'],
                    now_rank=total_count['now_rank'],
                    his_rank=total_count['his_rank'],
                )
                session.add(new_state)
                video.last_get_state_time = datetime.datetime.now()
                logger.info(f"{video.aid} {video.title} online: {online_count}, total: {new_state.view}")
                session.commit()
            except Exception as e:
                logger.error(f"写入数据库出错\n", e)
                session.rollback()




if __name__ == '__main__':
    watcher = StateWatcher()
    watcher.startWatchState()