import json

# 读取 JSON 文件
with open("Colorless_Cards.json", "r", encoding="utf-8") as f:
    cards = json.load(f)

# 遍历 JSON 数据并修改字段
for card in cards:
    # 处理 rarity 字段
    if card.get("rarity") == "Starter":
        card["rarity"] = "BASIC"

    # 新增字段
    card["exhausts"] = "Exhaust" in card.get("description", "")
    card["is_playable"] = "Unplayable" not in card.get("description", "")
    card["ethereal"] = "Ethereal" in card.get("description", "")
    card["upgrades"] = 0

    # 删除 description 字段
    if "description" in card:
        del card["description"]

# 保存回原 JSON 文件
with open("Colorless_Cards.json", "w", encoding="utf-8") as f:
    json.dump(cards, f, ensure_ascii=False, indent=4)

print("JSON 文件已更新并保存。")
