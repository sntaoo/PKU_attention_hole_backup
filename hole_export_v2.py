import json
import time
import random
import requests
from datetime import datetime

# Input your pkuhelper user token here
USER_TOKEN = "your user token here"

r = requests.get(
    "https://pkuhelper.pku.edu.cn/services/pkuhole/api.php?action=getattention&PKUHelperAPI=3.0&jsapiver=null-111111&user_token="+USER_TOKEN)
attentions = r.json()
if attentions["code"] != 0:
    print(attentions)
    raise Exception("get attention request failed")
attentions_data = attentions["data"]
n = len(attentions_data)
print("exporting " + str(n) + " holes...")
export = []
ready_to_try = []
def get_hole_content(i, pid, depth):
    try:
        if depth >= 7: # 增加重试七次，每次休眠
            print(f"Fetch hole {pid} failed after {depth} attempts!")
            ready_to_try.append(pid) # 如果失败，添加到列表末尾，留待之后尝试
            time.sleep(random.uniform(20.5,25.5))
            return False
        time.sleep(random.uniform(0.2, 0.5))
        r2 = requests.get("https://pkuhelper.pku.edu.cn/services/pkuhole/api.php?action=getcomment&pid=" +
                        pid+"&PKUHelperAPI=3.0&jsapiver=null-111111&user_token="+USER_TOKEN)
        comments = r2.json()
        if comments["code"] != 0:
            ready_to_try.append(pid)
            raise Exception("get comments (pid=" + pid + ") request failed")
        export.append({"post": attentions_data[i], "comments": comments["data"]})
        print(f"{i+1}/{n} finished export pid={pid}")
        return True
    except Exception as e:
        return get_hole_content(i, pid, depth+1)

for elem in attentions_data:
    ready_to_try.append(elem["pid"])

continuously_failure = 0 # 连着失败的次数。如果连着失败2次，休眠30秒
if ready_to_try:
    for i,pid in enumerate(ready_to_try):
        if get_hole_content(i, pid, 0): 
        # 如果获取失败,会在函数中被再次添加到list末尾留待重新获取，直到所有的树洞都获取完成
            continuously_failure = 0
        else:
            continuously_failure += 1
            if continuously_failure >= 2:
                time.sleep(30)
                continuously_failure = 0

# 将所有的树洞都装进list后再写入文件，如果树洞不是dramatically多，应该是不会爆内存的。因此不另写数据分片逻辑
export_txt = ""
for item in export:
    post = item["post"]
    image_url = "[图片] https://pkuhelper.pku.edu.cn/services/pkuhole/images/" + \
        post["url"] + "\n" if len(post["url"]) > 0 else ""
    time_str = datetime.fromtimestamp(
        int(post["timestamp"])).strftime('%Y-%m-%d %H:%M:%S')
    export_txt += "#{}\n{}\n{}（{} {}关注 {}回复）\n".format(
        post["pid"], post["text"], image_url, time_str, post["likenum"], post["reply"])
    for comment in item["comments"]:
        time_str = datetime.fromtimestamp(
            int(comment["timestamp"])).strftime('%Y-%m-%d %H:%M:%S')
        export_txt += "{}\n{}\n".format(time_str, comment["text"])
    export_txt += "\n========================================================\n\n"


with open("export.txt", "w") as f:
    f.write(export_txt.encode('GBK','ignore').decode('GBK'))


with open("export.json", "w") as f:
    f.write(json.dumps(export))
