import json
import time
import random
import requests
from datetime import datetime
from json_util import obj_stringfy

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
pid2ind = {}
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
            # 如果获取失败,会在函数中被再次添加到list末尾留待重新获取，直到所有的树洞都获取完成
            ready_to_try.append(pid)
            raise Exception("get comments (pid=" + pid + ") request failed")
        export.append({"post": attentions_data[pid2ind[pid]], "comments": comments["data"]})
        return True
    except Exception as e:
        return get_hole_content(i, pid, depth+1)

for elem in attentions_data:
    ready_to_try.append(elem["pid"])


for i, pid in enumerate(ready_to_try):
    pid2ind[pid] = i

continuously_failure = 0 # 连着失败的次数。如果连着失败2次，休眠30秒

with open("export.txt", "w", encoding="utf8") as holes:
    if ready_to_try:
        for i, pid in enumerate(ready_to_try):
            if get_hole_content(i, pid, 0): 
                continuously_failure = 0
                # 获取成功，将新添加的json对象写入文件
                obj = export[-1]
                holes.write(obj_stringfy(obj))
                holes.write("\n========================================\n\n")
                holes.flush()
                print(f"{i+1}/{n} finished export pid={pid}")
            else:
                # 获取失败，连续失败次数加1，如果连续失败两次，休眠30秒躲过网络拦截
                continuously_failure += 1
                if continuously_failure >= 2:
                    time.sleep(30)
                    continuously_failure = 0
