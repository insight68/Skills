#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《尼尔斯骑鹅旅行记》游戏进度管理器
Save Manager for "The Wonderful Adventures of Nils"

功能：
- 自动保存进度
- 多槽位存档
- 存档导入/导出
- 进度统计
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class SaveManager:
    """游戏存档管理器"""

    def __init__(self, save_dir: str = "."):
        """
        初始化存档管理器

        Args:
            save_dir: 存档目录路径
        """
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.meta_file = self.save_dir / "saves_meta.json"

    def save_game(self, slot_name: str, game_data: Dict) -> str:
        """
        保存游戏进度

        Args:
            slot_name: 存档槽名称
            game_data: 游戏数据

        Returns:
            存档文件路径
        """
        save_file = self.save_dir / f"{slot_name}.json"

        save_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "version": "1.0",
                "slot_name": slot_name
            },
            "game_data": game_data
        }

        with open(save_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)

        # 更新元数据
        self._update_metadata(slot_name, save_data["metadata"])

        return str(save_file)

    def load_game(self, slot_name: str) -> Optional[Dict]:
        """
        加载游戏进度

        Args:
            slot_name: 存档槽名称

        Returns:
            游戏数据，如果存档不存在则返回None
        """
        save_file = self.save_dir / f"{slot_name}.json"

        if not save_file.exists():
            return None

        with open(save_file, 'r', encoding='utf-8') as f:
            save_data = json.load(f)

        return save_data.get("game_data")

    def delete_save(self, slot_name: str) -> bool:
        """
        删除存档

        Args:
            slot_name: 存档槽名称

        Returns:
            是否成功删除
        """
        save_file = self.save_dir / f"{slot_name}.json"

        if save_file.exists():
            save_file.unlink()
            self._remove_metadata(slot_name)
            return True

        return False

    def list_saves(self) -> List[Dict[str, Any]]:
        """
        列出所有存档

        Returns:
            存档信息列表
        """
        saves = []

        for save_file in self.save_dir.glob("*.json"):
            if save_file.name == "saves_meta.json":
                continue

            try:
                with open(save_file, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)

                metadata = save_data.get("metadata", {})
                game_data = save_data.get("game_data", {})

                saves.append({
                    "name": save_file.stem,
                    "timestamp": metadata.get("timestamp", "未知"),
                    "version": metadata.get("version", "未知"),
                    "current_scene": game_data.get("current_scene", "未知"),
                    "chapter": self._get_chapter_name(game_data.get("current_scene", "")),
                    "hp": game_data.get("hp", 100),
                    "morality": game_data.get("morality", 50),
                    "knowledge": game_data.get("knowledge", 0),
                    "achievements_count": len(game_data.get("achievements", []))
                })
            except Exception as e:
                print(f"读取存档失败 {save_file}: {e}")

        return sorted(saves, key=lambda x: x["timestamp"], reverse=True)

    def export_save(self, slot_name: str, export_path: str) -> bool:
        """
        导出存档

        Args:
            slot_name: 存档槽名称
            export_path: 导出路径

        Returns:
            是否成功导出
        """
        save_file = self.save_dir / f"{slot_name}.json"

        if not save_file.exists():
            return False

        import shutil
        shutil.copy2(save_file, export_path)
        return True

    def import_save(self, import_path: str, slot_name: str) -> bool:
        """
        导入存档

        Args:
            import_path: 导入路径
            slot_name: 存档槽名称

        Returns:
            是否成功导入
        """
        if not os.path.exists(import_path):
            return False

        import shutil
        target_path = self.save_dir / f"{slot_name}.json"
        shutil.copy2(import_path, target_path)

        # 更新元数据
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            self._update_metadata(slot_name, save_data.get("metadata", {}))
        except:
            pass

        return True

    def get_playtime_stats(self) -> Dict[str, Any]:
        """
        获取游戏统计信息

        Returns:
            统计信息
        """
        saves = self.list_saves()

        if not saves:
            return {
                "total_saves": 0,
                "latest_playtime": None,
                "total_achievements": 0
            }

        latest = saves[0] if saves else None
        total_achievements = set()

        for save in saves:
            # 这里需要从游戏数据中提取成就
            # 简化处理，只记录数量
            pass

        return {
            "total_saves": len(saves),
            "latest_save": latest,
            "latest_playtime": latest.get("timestamp") if latest else None
        }

    def _update_metadata(self, slot_name: str, metadata: Dict):
        """更新存档元数据"""
        meta = {}

        if self.meta_file.exists():
            with open(self.meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)

        meta[slot_name] = metadata

        with open(self.meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    def _remove_metadata(self, slot_name: str):
        """移除存档元数据"""
        if not self.meta_file.exists():
            return

        with open(self.meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if slot_name in meta:
            del meta[slot_name]

        with open(self.meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    def _get_chapter_name(self, scene_id: str) -> str:
        """根据场景ID获取章节名称"""
        chapter_map = {
            "start": "序幕",
            "tutorial": "游戏指南",
            "chapter1": "第一章：变小的人",
            "chapter2": "第二章：初遇雁群",
            "chapter3": "第三章：夜晚的营地",
            "chapter4": "第四章：奥斯莫山区",
            "chapter5": "第五章：风暴来袭",
            "chapter6": "第六章：风暴后的平静",
            "chapter7": "第七章：北方的呼唤",
            "chapter8": "第八章：凯布讷山的考验"
        }

        for key, value in chapter_map.items():
            if scene_id.startswith(key):
                return value

        return "未知章节"


class AutoSaveManager:
    """自动保存管理器"""

    def __init__(self, save_manager: SaveManager, auto_save_interval: int = 5):
        """
        初始化自动保存管理器

        Args:
            save_manager: 存档管理器实例
            auto_save_interval: 自动保存间隔（每个场景变化后）
        """
        self.save_manager = save_manager
        self.auto_save_interval = auto_save_interval
        self.scene_count = 0

    def on_scene_change(self, slot_name: str, game_data: Dict):
        """
        场景变化时触发

        Args:
            slot_name: 存档槽名称
            game_data: 游戏数据
        """
        self.scene_count += 1

        if self.scene_count >= self.auto_save_interval:
            self.save_manager.save_game(slot_name, game_data)
            self.scene_count = 0

    def force_save(self, slot_name: str, game_data: Dict):
        """
        强制保存

        Args:
            slot_name: 存档槽名称
            game_data: 游戏数据
        """
        self.save_manager.save_game(slot_name, game_data)
        self.scene_count = 0


def format_playtime(timestamp: str) -> str:
    """格式化游戏时间"""
    try:
        dt = datetime.fromisoformat(timestamp)
        now = datetime.now()
        delta = now - dt

        if delta.days > 0:
            return f"{delta.days}天前"
        elif delta.seconds >= 3600:
            hours = delta.seconds // 3600
            return f"{hours}小时前"
        elif delta.seconds >= 60:
            minutes = delta.seconds // 60
            return f"{minutes}分钟前"
        else:
            return "刚刚"
    except:
        return timestamp


if __name__ == "__main__":
    # 测试代码
    print("存档管理器测试")
    print("=" * 50)

    manager = SaveManager("./test_saves")

    # 创建测试存档
    test_data = {
        "current_scene": "chapter1_intro",
        "hp": 100,
        "morality": 50,
        "knowledge": 100
    }

    manager.save_game("test", test_data)
    print("创建测试存档成功")

    # 列出存档
    saves = manager.list_saves()
    print(f"\n存档列表 ({len(saves)} 个):")
    for save in saves:
        print(f"  - {save['name']}: {save['chapter']} ({save['timestamp']})")

    # 加载存档
    loaded = manager.load_game("test")
    print(f"\n加载存档: {loaded}")
