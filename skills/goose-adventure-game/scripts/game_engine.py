#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《尼尔斯骑鹅旅行记》文字冒险游戏引擎
Text Adventure Game Engine for "The Wonderful Adventures of Nils"

支持功能：
- 剧情节点系统
- 选择分支
- 状态管理（生命值、道德值、大小值、知识值）
- 成就系统
- 进度保存/加载
- 物品栏管理
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class GameState:
    """游戏状态数据类"""
    current_scene: str = "start"  # 当前场景ID
    hp: int = 100  # 生命值 (0-100)
    morality: int = 50  # 道德值 (0-100, 低=自私, 高=善良)
    size: int = 10  # 大小值 (0-100, 小=拇指大小, 大=正常)
    knowledge: int = 0  # 知识值 (0-1000)
    inventory: List[str] = None  # 物品栏
    achievements: List[str] = None  # 成就列表
    flags: Dict[str, bool] = None  # 事件标志
    history: List[str] = None  # 历史记录

    def __post_init__(self):
        if self.inventory is None:
            self.inventory = []
        if self.achievements is None:
            self.achievements = []
        if self.flags is None:
            self.flags = {}
        if self.history is None:
            self.history = []


@dataclass
class Choice:
    """选项数据类"""
    text: str  # 选项显示文本
    next_scene: str  # 跳转的场景ID
    requirements: Optional[Dict[str, Any]] = None  # 触发条件
    effects: Optional[Dict[str, Any]] = None  # 选择后的效果
    moral_change: Optional[int] = None  # 道德值变化
    knowledge_gain: Optional[int] = None  # 知识值获得


@dataclass
class Scene:
    """场景数据类"""
    id: str  # 场景ID
    title: str  # 场景标题
    description: str  # 场景描述
    choices: List[Choice]  # 选项列表
    image_prompt: Optional[str] = None  # 配图提示
    music: Optional[str] = None  # 背景音乐
    narrator: Optional[str] = None  # 旁白风格


class GameEngine:
    """游戏引擎主类"""

    def __init__(self, script_data: Dict, save_dir: str = "."):
        """
        初始化游戏引擎

        Args:
            script_data: 游戏剧本数据
            save_dir: 存档目录
        """
        self.script = script_data
        self.save_dir = save_dir
        self.state = GameState()
        self.scenes: Dict[str, Scene] = {}
        self._load_scenes()

    def _load_scenes(self):
        """加载场景数据"""
        for scene_data in self.script.get("scenes", []):
            choices = []
            for choice_data in scene_data.get("choices", []):
                choices.append(Choice(
                    text=choice_data["text"],
                    next_scene=choice_data["next_scene"],
                    requirements=choice_data.get("requirements"),
                    effects=choice_data.get("effects"),
                    moral_change=choice_data.get("moral_change"),
                    knowledge_gain=choice_data.get("knowledge_gain")
                ))
            self.scenes[scene_data["id"]] = Scene(
                id=scene_data["id"],
                title=scene_data["title"],
                description=scene_data["description"],
                choices=choices,
                image_prompt=scene_data.get("image_prompt"),
                music=scene_data.get("music"),
                narrator=scene_data.get("narrator")
            )

    def get_current_scene(self) -> Optional[Scene]:
        """获取当前场景"""
        return self.scenes.get(self.state.current_scene)

    def get_available_choices(self) -> List[Choice]:
        """获取当前可用的选项"""
        scene = self.get_current_scene()
        if not scene:
            return []

        available = []
        for choice in scene.choices:
            if self._check_requirements(choice.requirements):
                available.append(choice)
        return available

    def _check_requirements(self, requirements: Optional[Dict]) -> bool:
        """检查选项是否满足触发条件"""
        if not requirements:
            return True

        # 检查物品
        if "has_item" in requirements:
            if requirements["has_item"] not in self.state.inventory:
                return False

        # 检查标志
        if "flag" in requirements:
            flag_name, flag_value = requirements["flag"]
            if self.state.flags.get(flag_name) != flag_value:
                return False

        # 检查数值范围
        if "morality_min" in requirements:
            if self.state.morality < requirements["morality_min"]:
                return False

        if "morality_max" in requirements:
            if self.state.morality > requirements["morality_max"]:
                return False

        if "size_min" in requirements:
            if self.state.size < requirements["size_min"]:
                return False

        if "size_max" in requirements:
            if self.state.size > requirements["size_max"]:
                return False

        # 检查成就
        if "has_achievement" in requirements:
            if requirements["has_achievement"] not in self.state.achievements:
                return False

        return True

    def make_choice(self, choice_index: int) -> bool:
        """
        做出选择

        Args:
            choice_index: 选项索引

        Returns:
            是否成功执行选择
        """
        choices = self.get_available_choices()
        if choice_index < 0 or choice_index >= len(choices):
            return False

        choice = choices[choice_index]

        # 记录历史
        self.state.history.append(f"{self.state.current_scene}:{choice.text}")

        # 应用效果
        if choice.effects:
            self._apply_effects(choice.effects)

        # 道德值变化
        if choice.moral_change is not None:
            self.state.morality = max(0, min(100, self.state.morality + choice.moral_change))

        # 知识值获得
        if choice.knowledge_gain is not None:
            self.state.knowledge += choice.knowledge_gain
            self._check_knowledge_achievements()

        # 跳转到下一场景
        self.state.current_scene = choice.next_scene

        return True

    def _apply_effects(self, effects: Dict):
        """应用选择效果"""
        if "add_item" in effects:
            item = effects["add_item"]
            if item not in self.state.inventory:
                self.state.inventory.append(item)

        if "remove_item" in effects:
            item = effects["remove_item"]
            if item in self.state.inventory:
                self.state.inventory.remove(item)

        if "hp_change" in effects:
            self.state.hp = max(0, min(100, self.state.hp + effects["hp_change"]))

        if "size_change" in effects:
            self.state.size = max(0, min(100, self.state.size + effects["size_change"]))

        if "set_flag" in effects:
            for flag, value in effects["set_flag"].items():
                self.state.flags[flag] = value

        if "add_achievement" in effects:
            achievement = effects["add_achievement"]
            if achievement not in self.state.achievements:
                self.state.achievements.append(achievement)

        if "game_over" in effects:
            self.state.current_scene = "game_over"

    def _check_knowledge_achievements(self):
        """检查知识成就"""
        if self.state.knowledge >= 100 and "自然观察者" not in self.state.achievements:
            self.state.achievements.append("自然观察者")
        if self.state.knowledge >= 300 and "小小博物学家" not in self.state.achievements:
            self.state.achievements.append("小小博物学家")
        if self.state.knowledge >= 500 and "地理大师" not in self.state.achievements:
            self.state.achievements.append("地理大师")
        if self.state.knowledge >= 800 and "智慧之星" not in self.state.achievements:
            self.state.achievements.append("智慧之星")

    def save_game(self, slot_name: str = "autosave") -> str:
        """
        保存游戏

        Args:
            slot_name: 存档槽名称

        Returns:
            存档文件路径
        """
        os.makedirs(self.save_dir, exist_ok=True)
        save_file = os.path.join(self.save_dir, f"{slot_name}.json")

        save_data = {
            "state": asdict(self.state),
            "timestamp": datetime.now().isoformat(),
            "version": "1.0"
        }

        with open(save_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)

        return save_file

    def load_game(self, slot_name: str = "autosave") -> bool:
        """
        加载游戏

        Args:
            slot_name: 存档槽名称

        Returns:
            是否成功加载
        """
        save_file = os.path.join(self.save_dir, f"{slot_name}.json")

        if not os.path.exists(save_file):
            return False

        with open(save_file, 'r', encoding='utf-8') as f:
            save_data = json.load(f)

        self.state = GameState(**save_data["state"])
        return True

    def get_save_files(self) -> List[Dict[str, str]]:
        """获取所有存档文件信息"""
        saves = []
        if not os.path.exists(self.save_dir):
            return saves

        for filename in os.listdir(self.save_dir):
            if filename.endswith(".json"):
                save_file = os.path.join(self.save_dir, filename)
                try:
                    with open(save_file, 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                    saves.append({
                        "name": filename[:-5],  # 移除.json后缀
                        "timestamp": save_data.get("timestamp", "未知"),
                        "scene": save_data["state"]["current_scene"]
                    })
                except:
                    pass

        return sorted(saves, key=lambda x: x["timestamp"], reverse=True)

    def render_scene(self) -> Dict[str, Any]:
        """
        渲染当前场景

        Returns:
            包含场景信息的字典
        """
        scene = self.get_current_scene()
        if not scene:
            return {"error": "场景不存在"}

        return {
            "title": scene.title,
            "description": scene.description,
            "choices": [{"index": i, "text": c.text} for i, c in enumerate(self.get_available_choices())],
            "state": {
                "hp": self.state.hp,
                "morality": self.state.morality,
                "size": self.state.size,
                "knowledge": self.state.knowledge,
                "inventory": self.state.inventory,
                "achievements": self.state.achievements
            },
            "image_prompt": scene.image_prompt,
            "music": scene.music,
            "narrator": scene.narrator
        }

    def get_ending(self) -> Optional[Dict]:
        """
        根据游戏状态计算结局

        Returns:
            结局信息
        """
        endings = self.script.get("endings", [])

        # 检查特殊结局条件
        for ending in endings:
            if ending.get("requirements"):
                if self._check_requirements(ending["requirements"]):
                    return ending

        # 默认根据道德值和大小值判断结局
        if self.state.morality >= 70:
            return endings[0] if len(endings) > 0 else {"title": "完美结局", "description": "你成长为了一个善良、勇敢的人"}
        elif self.state.morality >= 40:
            return endings[1] if len(endings) > 1 else {"title": "普通结局", "description": "你学到了很多，但还有进步空间"}
        else:
            return endings[2] if len(endings) > 2 else {"title": "需要改进", "description": "你还需要学会关心他人"}


def load_script_from_file(script_path: str) -> Dict:
    """从文件加载游戏脚本"""
    with open(script_path, 'r', encoding='utf-8') as f:
        return json.load(f)


if __name__ == "__main__":
    # 测试代码
    print("《尼尔斯骑鹅旅行记》游戏引擎 v1.0")
    print("=" * 50)
    print("这是一个文字冒险游戏引擎")
    print("请使用完整的游戏脚本来运行游戏")
