import json
from typing import Dict, List, Any, Union
from pathlib import Path
from dataclasses import asdict, is_dataclass

class JsonUtils:
    @staticmethod
    def load_json(file_path: str) -> Union[Dict[str, Any], List[Any]]:
        """
        加载 JSON 文件
        :param file_path: JSON 文件路径
        :return: 解析后的字典或列表
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: JSON file not found at {file_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in file {file_path}")
            return {}
        except Exception as e:
            print(f"Error: Failed to load JSON file {file_path}: {e}")
            return {}

    @staticmethod
    def save_json(file_path: str, data: Union[Dict[str, Any], List[Any]]) -> bool:
        """
        保存数据到 JSON 文件
        :param file_path: JSON 文件路径
        :param data: 要保存的数据（字典或列表）
        :return: 是否保存成功
        """
        try:
            # 确保目录存在
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error: Failed to save JSON file {file_path}: {e}")
            return False

    @staticmethod
    def serialize_to_str(data: Any) -> str:
        """
        序列化对象为 JSON 字符串
        :param data: 要序列化的对象（字典、列表等）
        :return: JSON 字符串
        """
        try:
            # 检查输入数据是否是一个 dataclass 实例或包含 dataclass 实例的列表
            if is_dataclass(data):
                # 单个数据类实例
                data = asdict(data)
            elif isinstance(data, list):
                # 列表，检查每个元素
                data = [asdict(item) if is_dataclass(item) else item for item in data if item is not None]
            return json.dumps(data, ensure_ascii=False)
        except Exception as e:
            print(f"Error: Failed to serialize object to string: {e}")
            return ""

    @staticmethod
    def deserialize_from_str(json_str: str, data_class: Any) -> Any:
        """
        反序列化 JSON 字符串为 Python 对象
        :param json_str: JSON 字符串
        :param data_class: 目标数据类型（如 Monster）
        :return: 反序列化后的对象或对象列表
        """
        if not json_str:
            print("Error: JSON string is empty or None")
            return None
        try:
            # 将 JSON 字符串解析为 Python 对象（字典或列表）
            data = json.loads(json_str)

            # 如果是列表，逐个反序列化为 data_class 实例
            if isinstance(data, list):
                return [data_class(**item) for item in data]
            # 如果是字典，直接反序列化为 data_class 实例
            elif isinstance(data, dict):
                return data_class(**data)
            else:
                raise ValueError("Invalid JSON format for deserialization")
        except Exception as e:
            print(f"Error: Failed to deserialize string to object: {e}")
            return None