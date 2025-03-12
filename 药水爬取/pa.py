import os
import json
import requests
from bs4 import BeautifulSoup


def get_potions():
    url = "https://slay-the-spire.fandom.com/wiki/Potions"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Failed to retrieve the page")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    potion_data = []

    # 找到药水表格
    table = soup.find("table", {"class": "article-table"})
    if not table:
        print("Potion table not found!")
        return

    rows = table.find_all("tr")[1:]  # 跳过表头

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 2:
            continue

        img_tag = cols[0].find("img")
        potion_name = cols[1].text.strip()  # 直接从 td 获取名称

        img_url = None
        if img_tag:
            img_url = img_tag.get("data-src") or img_tag.get("src")  # 处理懒加载图片
            if img_url:
                img_url = img_url.split("/revision")[0]  # 去掉 URL 后的版本信息

        if potion_name and img_url:
            print(f"Found potion: {potion_name}, Image URL: {img_url}")  # 调试输出
            potion_data.append({"name": potion_name, "image": img_url})

    return potion_data


def save_potions(potion_data):
    if not os.path.exists("potions"):  # 创建存储目录
        os.makedirs("potions")

    # 保存 JSON 数据
    with open("potions/potions.json", "w", encoding="utf-8") as f:
        json.dump(potion_data, f, ensure_ascii=False, indent=4)

    # 下载图片
    for potion in potion_data:
        img_url = potion["image"]
        if not img_url:
            print(f"Skipping {potion['name']} due to missing image URL")
            continue

        img_name = f"potions/{potion['name'].replace(' ', '_')}.png"

        try:
            img_data = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"}).content
            with open(img_name, "wb") as img_file:
                img_file.write(img_data)
                print(f"Downloaded: {img_name}")
        except Exception as e:
            print(f"Failed to download {img_name}: {e}")


if __name__ == "__main__":
    potions = get_potions()
    if potions:
        save_potions(potions)
        print("All potions saved successfully!")
import os
import json


def rename_potion_files(directory="potions"):
    if not os.path.exists(directory):
        print("Directory not found!")
        return

    potion_data = []

    for file in os.listdir(directory):
        if file.endswith(".png"):
            old_path = os.path.join(directory, file)
            new_name = file.replace("_", " ")[:-4]  # 去掉 .png 后缀
            new_path = os.path.join(directory, new_name + ".png")

            os.rename(old_path, new_path)
            potion_data.append({"name": new_name})
            print(f"Renamed: {file} -> {new_name}.png")

    json_path = os.path.join(directory, "potions.json")
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(potion_data, json_file, ensure_ascii=False, indent=4)

    print(f"Potion names saved to {json_path}")


if __name__ == "__main__":
    rename_potion_files()
