import time

def get_format_time(time_stamp):
    time_local = time.localtime(int(time_stamp))
    return time.strftime("%Y-%m-%d %H:%M:%S", time_local)


def get_post(obj):
    post = obj['post']
    pid = "#" + post['pid'] + "\n"
    text = post['text'] + "\n"
    pic_url = ""
    if "image" == post['type']:
        pic_url = "[树洞图片]https://pkuhelper.pku.edu.cn/services/pkuhole/images/" + \
            post['url'] + "\n"
    tail = f"({get_format_time(post['timestamp'])} {post['likenum']}关注 {post['reply']}回复)\n"
    return (pid + text + pic_url + tail)


def get_comments(obj):
    comments = obj['comments']
    ret = ""
    for comment in comments:
        ret += get_format_time(comment['timestamp']) + \
            "\n" + comment['text'] + "\n"
    return ret

# 将json对象转为可写入文件的string
def obj_stringfy(obj):
    return get_post(obj) + get_comments(obj)
