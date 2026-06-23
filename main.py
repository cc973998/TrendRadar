import requests
import os
from datetime import datetime

# 钉钉推送函数
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

# ---------- 使用免费公开接口（百度热搜） ----------
def get_hot_news():
    try:
        # 这个接口无需 Key，返回百度热搜 JSON
        url = "https://api.vvhan.com/api/hot"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # 检查返回状态
        if data.get('success') or data.get('code') == 200:
            # 提取热搜列表
            news_list = data.get('data', [])
            if isinstance(news_list, list) and len(news_list) > 0:
                print(f"✅ 成功获取 {len(news_list)} 条热点新闻")
                return news_list
            else:
                print(f"⚠️ 返回的数据格式异常：{data}")
                return []
        else:
            print(f"❌ API 返回错误：{data.get('msg', data)}")
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
        # 根据实际 JSON 结构提取标题和来源
        title = item.get('title', item.get('name', '无标题'))
        source = item.get('source', item.get('platform', '百度热搜'))
        date = today  # 接口不提供日期，用当天
        content += f"{idx}、{date}，{source}：{title}\n\n"

    send_to_dingtalk(content)

if __name__ == "__main__":
    main()
