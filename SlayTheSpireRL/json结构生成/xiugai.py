import json

# 读取 JSON 文件
with open("cards.json", "r", encoding="utf-8") as f:
    cards = json.load(f)

# 遍历 JSON 数据并修改字段
for card in cards:

    card["has_target"] = True


# 保存回原 JSON 文件
with open("cards.json", "w", encoding="utf-8") as f:
    json.dump(cards, f, ensure_ascii=False, indent=4)

print("JSON 文件已更新并保存。")
