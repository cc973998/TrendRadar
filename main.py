import requests
import yaml
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

# 获取热点数据
def get_hot_news():
    try:
        # 使用免费热点API
        url = "https://api.newsnow.today/api/v1/hot"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # 提取新闻列表
        news_list = data.get('data', [])
        print(f"✅ 共获取到 {len(news_list)} 条热点新闻")
        return news_list
    except Exception as e:
        print(f"❌ 获取热点失败：{e}")
        return []

# 读取关键词配置
def load_keywords():
    try:
        with open('config/frequency_words.txt', 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
        
        # 过滤掉空行和注释行
        keywords = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('['):
                keywords.append(line)
        
        print(f"✅ 共加载 {len(keywords)} 个关键词：{keywords}")
        return keywords
    except Exception as e:
        print(f"⚠️ 读取关键词文件失败：{e}")
        return []

# 主函数
def main():
    today = datetime.now().strftime('%m月%d日')
    
    # 1. 获取热点
    news_list = get_hot_news()
    if not news_list:
        send_to_dingtalk(f"每天一分钟，热点全掌握（{today}）\n\n暂无热点数据，请稍后查看。")
        return
    
    # 2. 读取关键词
    keywords = load_keywords()
    if not keywords:
        # 如果没有关键词，则推送所有新闻
        matched = news_list[:10]
        print("⚠️ 未设置关键词，推送全部新闻")
    else:
        # 3. 关键词筛选
        matched = []
        for item in news_list:
            title = item.get('title', '')
            # 只要标题包含任意关键词就匹配
            for keyword in keywords:
                if keyword in title:
                    matched.append(item)
                    break
    
    # 4. 限制数量（最多10条）
    matched = matched[:10]
    print(f"✅ 筛选后匹配 {len(matched)} 条新闻")
    
    # 5. 构建推送内容
    if not matched:
        content = f"每天一分钟，热点全掌握（{today}）\n\n今日无匹配关键词的热点新闻。"
    else:
        content = f"每天一分钟，热点全掌握（{today}）\n\n"
        for idx, item in enumerate(matched, 1):
            title = item.get('title', '')
            source = item.get('source', item.get('platform', '未知来源'))
            date = item.get('date', today)
            content += f"{idx}、{date}，{source}：{title}\n\n"
    
    # 6. 发送到钉钉
    send_to_dingtalk(content)

if __name__ == "__main__":
    main()
