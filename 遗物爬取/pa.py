import os
import json
import requests
from bs4 import BeautifulSoup

# 设置目标URL
URL = "https://slay-the-spire.fandom.com/wiki/Relics"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

# 创建保存图片的文件夹
IMAGE_DIR = "relics_images"
os.makedirs(IMAGE_DIR, exist_ok=True)


def download_image(image_url, filename):
    """下载图片并保存到本地"""
    response = requests.get(image_url, headers=HEADERS, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)


def scrape_relics():
    """爬取遗物名称和图片"""
    response = requests.get(URL, headers=HEADERS)
    if response.status_code != 200:
        print("Failed to fetch the webpage")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    relic_data = {}

    # 选择所有遗物的容器
    relics = soup.select(".article-table tbody tr")

    for relic in relics:
        cols = relic.find_all("td")
        if len(cols) < 2:
            continue

        # 遗物名称
        name_tag = cols[1].find("a")
        if not name_tag:
            continue
        relic_name = name_tag.text.strip()

        # 图片URL
        img_tag = cols[0].find("img")
        if not img_tag or not img_tag.has_attr("data-src"):
            continue
        img_url = img_tag["data-src"].split("/revision/")[0]  # 去除URL中的版本控制部分

        # 保存图片
        img_filename = os.path.join(IMAGE_DIR, f"{relic_name}.png")
        download_image(img_url, img_filename)

        # 存储数据
        relic_data[relic_name] = img_filename

    # 保存数据为JSON
    with open("relics.json", "w", encoding="utf-8") as json_file:
        json.dump(relic_data, json_file, ensure_ascii=False, indent=4)

    print(f"Scraped {len(relic_data)} relics successfully!")


if __name__ == "__main__":
    scrape_relics()