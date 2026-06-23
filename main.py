import requests
import os
from datetime import datetime

# 钉钉推送函数（不用改）
def send_to_dingtalk(content):
    webhook = os.environ.get('DINGTALK_WEBHOOK_URL')
    if not webhook:
        print("❌ 未设置 DINGTALK_WEBHOOK_URL")
        return False
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "每日热点",
            "text": content
        }
    }
    try:
        response = requests.post(webhook, json=data, timeout=10)
        if response.status_code == 200:
            print("✅ 推送成功！")
            return True
        else:
            print(f"❌ 推送失败：{response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 推送异常：{e}")
        return False

48e929092baf9ba4943088dd316331ae
def get_hot_news():
    try:
        # 使用更稳定的免费 API（替换了原来的 newsnow）
        url = "https://api.tianapi.com/guonei/index?key=请替换你的APIKey&num=10"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # 根据新 API 的数据格式解析
        if data.get('code') == 200:
            news_list = data.get('newslist', [])
            print(f"✅ 成功获取 {len(news_list)} 条热点新闻")
            return news_list
        else:
            print(f"❌ API 返回错误：{data.get('msg', '未知错误')}")
            return []
    except Exception as e:
        print(f"❌ 获取热点失败：{e}")
        return []

def main():
    today = datetime.now().strftime('%m月%d日')
    news_list = get_hot_news()

    if not news_list:
        send_to_dingtalk(f"每天一分钟，热点全掌握（{today}）\n\n暂无热点数据，请稍后查看。")
        return

    # 构建推送内容（取前10条）
    content = f"每天一分钟，热点全掌握（{today}）\n\n"
    for idx, item in enumerate(news_list[:10], 1):
        title = item.get('title', '无标题')
        source = item.get('source', '')
        date = item.get('ctime', today)
        content += f"{idx}、{date}，{source}：{title}\n\n"

    send_to_dingtalk(content)

if __name__ == "__main__":
    main()
