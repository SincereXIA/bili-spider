# 导入:
from sqlalchemy import Column, String, create_engine, Integer, CHAR, DateTime, ForeignKey,Text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from config import *

# 创建对象的基类:
Base = declarative_base()

class VideoInfo(Base):

    # 表的名字:
    __tablename__ = 'video_info'

    # 表的结构:
    aid = Column(Integer(), primary_key=True)
    bvid = Column(String(20))
    tid = Column(Integer(), ForeignKey('channel_info.tid'))
    zid = Column(Integer(), ForeignKey('zone_info.zid'))
    cid = Column(Integer(), nullable=True)
    title = Column(Text())
    pubdate = Column(DateTime())
    desc = Column(Text(), nullable=True) # 简介
    attribute = Column(Integer(), nullable=True)
    duration = Column(Integer())
    owner_id = Column(Integer(), ForeignKey('uploader_info.mid'))
    collect_time = Column(DateTime(), nullable=True)
    first_get_state_time = Column(DateTime, nullable=True)
    last_get_state_time = Column(DateTime,nullable=True)
    collect_id = Column(Integer(), autoincrement=True)

    states = relationship('VideoState', backref="video")


class ChannelInfo(Base):

    __tablename__ = 'channel_info'
    tid = Column(Integer(), primary_key=True)
    name = Column(String(100))
    subscribed_count = Column(Integer(), nullable=True)
    archive_count = Column(String(20), nullable=True)
    featured_count = Column(Integer(), nullable=True)
    cover = Column(Text(), nullable=True)

    videos = relationship('VideoInfo', backref = "channel")

class UploaderInfo(Base):

    __tablename__ = 'uploader_info'

    mid = Column(Integer(), primary_key=True)
    name = Column(String(100))
    face = Column(Text(), nullable=True)

    videos = relationship('VideoInfo', backref="uploader")


class VideoState(Base):

    __tablename__ = 'video_state'

    sid = Column(Integer(), primary_key=True, autoincrement=True)
    aid = Column(Integer(), ForeignKey('video_info.aid'))
    time = Column(DateTime())
    online = Column(Integer())
    view = Column(Integer())
    danmaku = Column(Integer(), nullable=True)
    reply = Column(Integer(), nullable=True)
    favorite = Column(Integer(), nullable=True)
    coin = Column(Integer(), nullable=True)
    share = Column(Integer(), nullable=True)
    like = Column(Integer(), nullable=True)
    dislike = Column(Integer(), nullable=True)
    now_rank = Column(Integer(), nullable=True)
    his_rank = Column(Integer(), nullable=True)

class ZoneInfo(Base):
    __tablename__ = "zone_info"
    zid = Column(Integer(), primary_key=True)
    name = Column(String(20), nullable=True)
    desc = Column(Text(), nullable=True)
    videos = relationship('VideoInfo', backref = "zone")

# 初始化数据库连接:
mysql_url = f"{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_ADDRESS}:{MYSQL_PORT}/{DATABASE_NAME}"
engine = create_engine('mysql+mysqlconnector://' + mysql_url)

# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)

if __name__ == '__main__':
    # 初始建表
    Base.metadata.create_all(engine)
