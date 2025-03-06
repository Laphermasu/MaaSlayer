import requests
from bs4 import BeautifulSoup
import json

# 目标网页URL
url = "https://slay-the-spire.fandom.com/wiki/Curse"

# 发送HTTP请求
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers)

# 检查请求是否成功
if response.status_code != 200:
    print(f"请求失败，状态码: {response.status_code}")
    exit()

# 解析HTML
soup = BeautifulSoup(response.text, "html.parser")

# 打印 HTML 以调试结构
print(soup.prettify())  # 用于调试，可以在此处查看页面结构

# 找到所有包含卡牌信息的元素
# 根据观察，卡牌信息并不一定在表格内，可能是在某些div或者特定的section中

# 我们可以尝试找到所有的卡牌条目
cards = []

# 示例中可以找到包含卡牌名称的元素，假设使用带有 "card" 或类似的class名称来提取
card_rows = soup.find_all("tr")  # 直接找所有<tr>标签（如果网页结构变化，可能需要改成其他标记）

# 调试：查看找到的条目数量
print(f"找到 {len(card_rows)} 行")

for row in card_rows:
    cols = row.find_all("td")
    if len(cols) >= 5:
        card_name = cols[0].get_text(strip=True)
        rarity = cols[2].get_text(strip=True)
        card_type = cols[3].get_text(strip=True)
        cost = cols[4].get_text(strip=True)

        # 解析描述（移除HTML标签）
        description_html = cols[5]
        for tag in description_html.find_all(["span", "a", "img"]):
            tag.unwrap()  # 移除 HTML 结构
        description = description_html.get_text(strip=True)

        cards.append({
            "name": card_name,
            "rarity": rarity,
            "type": card_type,
            "cost": cost,
            "description": description
        })

# 检查是否爬取到了数据
if not cards:
    print("未能爬取到卡牌数据，请检查网页结构。")
else:
    # 将数据保存为JSON文件
    with open("Curse.json", "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=4)

    print("卡牌数据已成功保存为 ironclad_cards.json")
