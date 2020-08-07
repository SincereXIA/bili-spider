from sqlalchemy import exists

from bilibili import VideoInfoSpider, PopularSpider

import database
from database import DBSession
from log import logger
import datetime


class VideoCollector:
    def _collect_video_info(self,tid, simple_info, session:DBSession, collect_id = 0):
        uploader_exists = session.query(
            exists().where(database.UploaderInfo.mid == simple_info['author_id'])
        ).scalar()
        if not uploader_exists:
            new_up = database.UploaderInfo(
                mid=simple_info['author_id'],
                name=simple_info['author_name'],
            )
            session.add(new_up)
            session.commit()
        new_video = database.VideoInfo(
            aid=simple_info['id'],
            bvid=simple_info['bvid'],
            tid=tid,
            title=simple_info['name'],
            owner_id=simple_info['author_id'],
            collect_time=datetime.datetime.now(),
            collect_id = collect_id
        )
        try:
            session.add(new_video)
            session.commit()
        except Exception as e:
            logger.error(f"向数据库中写入视频信息出错： {simple_info['name']}")
            session.rollback()


    def startCollect(self, detail = False):
        collect_id = 0
        popular_spider = PopularSpider()
        video_info_spider = VideoInfoSpider()
        channels = popular_spider.get_all_channels()
        session = DBSession()
        logger.info("开始写入数据库...")
        for channel in channels:
            try:
                channel_exists = session.query(
                    exists().where(database.ChannelInfo.tid == channel['id'])
                ).scalar()
                if not channel_exists:
                    new_channel = database.ChannelInfo(
                        tid=channel['id'],
                        name=channel['name'],
                        cover=channel['cover'],
                        subscribed_count=channel['subscribed_count'],
                        archive_count=channel['archive_count'],
                        featured_count=channel['featured_count'],
                    )
                    session.add(new_channel)
                    session.commit()
            except Exception:
                logger.error("频道写入失败，继续下一个频道")
                session.rollback()

        db_channels = session.query(database.ChannelInfo).all()
        for channel in db_channels:
            try:
                logger.info(f"开始爬取频道 {channel.tid}, {channel.name}"
                            f"top100 video")
                hot_videos = popular_spider.get_channel_hot_video(channel_id=channel.tid, video_num=20)
            except Exception:
                logger.error("频道获取失败，继续下一个频道")
                continue
            for video in hot_videos:  # 遍历所有推荐视频
                collect_id += 1
                if not detail:
                    self._collect_video_info(channel.tid, video, session, collect_id)
                    continue
                info = video_info_spider.get_video_info(video['id'])
                uploader_exists = session.query(
                    exists().where(database.UploaderInfo.mid == info['owner']['mid'])
                ).scalar()
                if not uploader_exists:
                    new_up = database.UploaderInfo(
                        mid=info['owner']['mid'],
                        name=info['owner']['name'],
                        face=info['owner']['face'],
                    )
                    session.add(new_up)
                    session.commit()
                zone_exists = session.query(
                    exists().where(database.ZoneInfo.zid == info['tid'])
                ).scalar()
                if not zone_exists:
                    new_zone = database.ZoneInfo(
                        zid=info['tid'],
                    )
                    session.add(new_zone)
                    session.commit()
                new_video = database.VideoInfo(
                    aid=info['aid'],
                    bvid=info['bvid'],
                    tid=channel.tid,
                    zid=info['tid'],
                    title=info['title'],
                    pubdate=datetime.datetime.fromtimestamp(info['pubdate']),
                    desc=info['desc'],
                    attribute=info['attribute'],
                    duration=info['duration'],
                    owner_id=info['owner']['mid'],
                    collect_time=datetime.datetime.now(),
                    collect_id=collect_id,
                )
                try:
                    session.add(new_video)
                    session.commit()
                except Exception as e:
                    logger.error(f"向数据库中写入视频信息出错： {info['title']}")
                    session.rollback()
        session.close()


if __name__ == '__main__':
    collector = VideoCollector()
    collector.startCollect()
