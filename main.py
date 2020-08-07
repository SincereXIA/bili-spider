from bilibili import VideoInfoSpider

if __name__ == '__main__':
    spider = VideoInfoSpider()
    cid = spider.get_cid(969075798)
    print(spider.get_online_count_and_tid(969075798, cid))
    spider.get_video_info(969075798)

