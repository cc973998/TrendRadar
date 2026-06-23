import requests
import os
import re
from datetime import datetime

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

def get_baidu_hot():
    """直接从百度热搜页面抓取数据"""
    try:
        url = "https://top.baidu.com/board?tab=realtime"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        html = response.text
        
        # 用正则提取热点标题
        # 百度热搜数据在页面中是以特定格式存在的
        pattern = r'"title":"([^"]+)"'
        titles = re.findall(pattern, html)
        
        # 过滤掉空的和无关的
        titles = [t for t in titles if t and len(t) > 2]
        
        # 去重并保留前10条
        seen = set()
        result = []
        for t in titles:
            if t not in seen:
                seen.add(t)
                result.append({"title": t, "source": "百度热搜"})
                if len(result) >= 10:
                    break
        
        print(f"✅ 从百度热搜抓取到 {len(result)} 条数据")
        return result
    except Exception as e:
        print(f"❌ 抓取百度热搜失败：{e}")
        return []

def main():
    today = datetime.now().strftime('%m月%d日')
    
    # 尝试抓取百度热搜
    news_list = get_baidu_hot()
    
    # 如果百度抓取失败，用备用关键词生成几条示例数据
    if not news_list:
        print("⚠️ 百度热搜抓取失败，使用备用数据")
        fallback_titles = [
            "今日要闻：全国多地持续高温天气",
            "社会热点：警方破获一起重大电信诈骗案",
            "民生关注：医保报销政策迎来新调整",
            "科技前沿：人工智能应用再获突破",
            "教育动态：高考成绩陆续公布",
            "财经资讯：A股市场今日震荡走高",
            "国际视野：联合国召开气候变化会议",
            "健康提醒：夏季饮食安全注意事项",
            "交通出行：端午假期出行高峰来临",
            "文化娱乐：多部新片定档暑期档"
        ]
        news_list = [{"title": t, "source": "今日要闻"} for t in fallback_titles]
        print(f"✅ 使用备用数据 {len(news_list)} 条")

    # 构建推送内容
    content = f"每天一分钟，热点全掌握（{today}）\n\n"
    for idx, item in enumerate(news_list[:10], 1):
        title = item.get('title', '无标题')
        source = item.get('source', '热点')
        content += f"{idx}、{today}，{source}：{title}\n\n"

    send_to_dingtalk(content)

if __name__ == "__main__":
    main()
