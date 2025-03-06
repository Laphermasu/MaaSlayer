import json

# 要合并的 JSON 文件列表
file_names = [
    "ironclad_cards.json",
    "Silent_Cards.json",
    "Defect_Cards.json",
    "Watcher_Cards.json",
    "Colorless_Cards.json"
]

# 存放所有卡牌数据的列表
all_cards = []

# 读取每个 JSON 文件并合并
for file_name in file_names:
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            data = json.load(file)
            all_cards.extend(data)  # 将每个文件的数据添加到 all_cards 中
            print(f"成功读取 {file_name}")
    except FileNotFoundError:
        print(f"文件 {file_name} 未找到")
    except json.JSONDecodeError:
        print(f"文件 {file_name} 无法解析")

# 将合并后的数据保存到一个新的 JSON 文件
with open("cards.json", "w", encoding="utf-8") as output_file:
    json.dump(all_cards, output_file, ensure_ascii=False, indent=4)

print("所有卡牌数据已成功合并并保存为 cards.json")
