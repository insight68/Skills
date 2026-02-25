#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text Adventure Game Engine

A flexible and extensible engine for creating text-based interactive fiction games.
Supports branching narratives, state management, conditional choices, and save/load functionality.

Author: Claude
Version: 2.0
License: MIT
"""

import json
import os
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from enum import Enum


class NarratorStyle(Enum):
    """Narrator style presets"""
    NEUTRAL = "neutral"
    FRIENDLY = "friendly"
    MYSTERIOUS = "mysterious"
    DRAMATIC = "dramatic"
    URGENT = "urgent"
    SERIOUS = "serious"
    INSPIRATIONAL = "inspirational"
    HUMOROUS = "humorous"


class MusicMood(Enum):
    """Background music mood presets"""
    PEACEFUL = "peaceful"
    ADVENTURE = "adventure"
    TENSE = "tense"
    MYSTERY = "mystery"
    TRIUMPHANT = "triumphant"
    MELANCHOLIC = "melancholic"
    CONFRONTATION = "confrontation"
    CAMPFIRE = "campfire"
    EMOTIONAL = "emotional"
    STORM = "storm"


@dataclass
class GameState:
    """Represents the current state of the game."""
    current_scene: str = "start"
    hp: int = 100
    morality: int = 50  # 0 = evil/selfish, 100 = good/selfless
    size: int = 100  # 0 = tiny, 100 = normal
    knowledge: int = 0
    gold: int = 0
    inventory: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    flags: Dict[str, Any] = field(default_factory=dict)
    history: List[str] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)  # Custom stat counters

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'GameState':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Choice:
    """Represents a player choice in a scene."""
    text: str
    next_scene: str
    requirements: Optional[Dict[str, Any]] = None
    effects: Optional[Dict[str, Any]] = None
    morality_change: Optional[int] = None
    knowledge_gain: Optional[int] = None
    gold_change: Optional[int] = None
    hp_change: Optional[int] = None


@dataclass
class Scene:
    """Represents a scene in the game."""
    id: str
    title: str
    description: str
    choices: List[Choice]
    image_prompt: Optional[str] = None
    music: Optional[str] = None
    narrator: Optional[str] = None
    on_enter: Optional[Dict[str, Any]] = None  # Effects when entering scene


class TextAdventureEngine:
    """
    Main game engine for text adventure games.

    Features:
    - Branching narrative with conditional choices
    - State management (HP, morality, knowledge, etc.)
    - Achievement system
    - Save/load functionality
    - Custom hooks and events
    """

    def __init__(self, script_data: Dict, save_dir: str = ".", debug: bool = False):
        """
        Initialize the game engine.

        Args:
            script_data: The game script data (dict)
            save_dir: Directory for save files
            debug: Enable debug output
        """
        self.script = script_data
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.state = GameState()
        self.scenes: Dict[str, Scene] = {}
        self.hooks: Dict[str, List[Callable]] = {
            "on_scene_enter": [],
            "on_scene_exit": [],
            "on_choice": [],
            "on_save": [],
            "on_load": []
        }
        self.debug = debug
        self._load_scenes()
        self._load_config()

    def _load_config(self):
        """Load game configuration."""
        self.config = self.script.get("config", {})
        self.game_info = self.script.get("game_info", {})

    def _load_scenes(self):
        """Load all scenes from script data."""
        for scene_data in self.script.get("scenes", []):
            choices = []
            for choice_data in scene_data.get("choices", []):
                choices.append(Choice(
                    text=choice_data["text"],
                    next_scene=choice_data["next_scene"],
                    requirements=choice_data.get("requirements"),
                    effects=choice_data.get("effects"),
                    morality_change=choice_data.get("morality_change"),
                    knowledge_gain=choice_data.get("knowledge_gain"),
                    gold_change=choice_data.get("gold_change"),
                    hp_change=choice_data.get("hp_change")
                ))
            self.scenes[scene_data["id"]] = Scene(
                id=scene_data["id"],
                title=scene_data["title"],
                description=scene_data["description"],
                choices=choices,
                image_prompt=scene_data.get("image_prompt"),
                music=scene_data.get("music"),
                narrator=scene_data.get("narrator"),
                on_enter=scene_data.get("on_enter")
            )

    def register_hook(self, event: str, callback: Callable):
        """Register a callback for a specific event."""
        if event in self.hooks:
            self.hooks[event].append(callback)

    def _trigger_hooks(self, event: str, *args, **kwargs):
        """Trigger all callbacks for an event."""
        for hook in self.hooks.get(event, []):
            hook(*args, **kwargs)

    def get_current_scene(self) -> Optional[Scene]:
        """Get the current scene object."""
        return self.scenes.get(self.state.current_scene)

    def get_available_choices(self) -> List[Choice]:
        """Get all choices that meet their requirements."""
        scene = self.get_current_scene()
        if not scene:
            return []

        available = []
        for choice in scene.choices:
            if self._check_requirements(choice.requirements):
                available.append(choice)
        return available

    def _check_requirements(self, requirements: Optional[Dict]) -> bool:
        """Check if requirements are met."""
        if not requirements:
            return True

        # Item checks
        if "has_item" in requirements:
            if requirements["has_item"] not in self.state.inventory:
                return False

        if "has_any_item" in requirements:
            if not any(item in self.state.inventory for item in requirements["has_any_item"]):
                return False

        if "has_all_items" in requirements:
            if not all(item in self.state.inventory for item in requirements["has_all_items"]):
                return False

        # Flag checks
        if "flag" in requirements:
            flag_name, flag_value = requirements["flag"]
            if self.state.flags.get(flag_name) != flag_value:
                return False

        if "flag_set" in requirements:
            if requirements["flag_set"] not in self.state.flags:
                return False

        if "flag_not_set" in requirements:
            if requirements["flag_not_set"] in self.state.flags:
                return False

        # Stat range checks
        for stat in ["morality", "size", "hp", "knowledge", "gold"]:
            if f"{stat}_min" in requirements:
                if getattr(self.state, stat) < requirements[f"{stat}_min"]:
                    return False
            if f"{stat}_max" in requirements:
                if getattr(self.state, stat) > requirements[f"{stat}_max"]:
                    return False

        # Custom stat checks
        if "stat_min" in requirements:
            stat_name, min_value = requirements["stat_min"]
            if self.state.stats.get(stat_name, 0) < min_value:
                return False

        # Achievement checks
        if "has_achievement" in requirements:
            if requirements["has_achievement"] not in self.state.achievements:
                return False

        # Scene history checks
        if "visited_scene" in requirements:
            if not any(req in h for h in self.state.history):
                return False

        return True

    def make_choice(self, choice_index: int) -> bool:
        """
        Make a choice and advance the game.

        Args:
            choice_index: Index of the choice to make

        Returns:
            True if successful, False otherwise
        """
        choices = self.get_available_choices()
        if choice_index < 0 or choice_index >= len(choices):
            return False

        choice = choices[choice_index]

        # Record history
        self.state.history.append(f"{self.state.current_scene}:{choice.text}")

        # Trigger exit hooks
        self._trigger_hooks("on_scene_exit", self.state.current_scene)

        # Apply choice effects
        if choice.effects:
            self._apply_effects(choice.effects)

        # Apply direct stat changes
        if choice.morality_change is not None:
            self.state.morality = max(0, min(100, self.state.morality + choice.morality_change))

        if choice.knowledge_gain is not None:
            self.state.knowledge += choice.knowledge_gain
            self._check_knowledge_achievements()

        if choice.gold_change is not None:
            self.state.gold = max(0, self.state.gold + choice.gold_change)

        if choice.hp_change is not None:
            self.state.hp = max(0, min(100, self.state.hp + choice.hp_change))

        # Trigger choice hooks
        self._trigger_hooks("on_choice", choice)

        # Move to next scene
        prev_scene = self.state.current_scene
        self.state.current_scene = choice.next_scene

        # Apply on_enter effects
        scene = self.get_current_scene()
        if scene and scene.on_enter:
            self._apply_effects(scene.on_enter)

        # Trigger enter hooks
        self._trigger_hooks("on_scene_enter", prev_scene, self.state.current_scene)

        return True

    def _apply_effects(self, effects: Dict):
        """Apply effects to game state."""
        # Item management
        if "add_item" in effects:
            item = effects["add_item"]
            if item not in self.state.inventory:
                self.state.inventory.append(item)

        if "add_items" in effects:
            for item in effects["add_items"]:
                if item not in self.state.inventory:
                    self.state.inventory.append(item)

        if "remove_item" in effects:
            item = effects["remove_item"]
            if item in self.state.inventory:
                self.state.inventory.remove(item)

        # Stat changes
        if "hp_change" in effects:
            self.state.hp = max(0, min(100, self.state.hp + effects["hp_change"]))

        if "morality_change" in effects:
            self.state.morality = max(0, min(100, self.state.morality + effects["morality_change"]))

        if "size_change" in effects:
            self.state.size = max(0, min(100, self.state.size + effects["size_change"]))

        if "gold_change" in effects:
            self.state.gold = max(0, self.state.gold + effects["gold_change"])

        if "knowledge_gain" in effects:
            self.state.knowledge += effects["knowledge_gain"]
            self._check_knowledge_achievements()

        # Custom stat changes
        if "stat_change" in effects:
            for stat, value in effects["stat_change"].items():
                self.state.stats[stat] = self.state.stats.get(stat, 0) + value

        # Flag management
        if "set_flag" in effects:
            for flag, value in effects["set_flag"].items():
                self.state.flags[flag] = value

        if "clear_flag" in effects:
            flag = effects["clear_flag"]
            if flag in self.state.flags:
                del self.state.flags[flag]

        # Achievement management
        if "add_achievement" in effects:
            achievement = effects["add_achievement"]
            if achievement not in self.state.achievements:
                self.state.achievements.append(achievement)

        # Special effects
        if "game_over" in effects:
            self.state.current_scene = "game_over"

        if "victory" in effects:
            self.state.current_scene = "victory"

    def _check_knowledge_achievements(self):
        """Check and award knowledge-based achievements."""
        milestones = self.config.get("knowledge_milestones", {})
        for threshold, achievement in milestones.items():
            if self.state.knowledge >= int(threshold) and achievement not in self.state.achievements:
                self.state.achievements.append(achievement)

    def save_game(self, slot_name: str = "autosave") -> str:
        """
        Save the game to a file.

        Args:
            slot_name: Name of the save slot

        Returns:
            Path to the save file
        """
        self._trigger_hooks("on_save", slot_name)

        save_file = self.save_dir / f"{slot_name}.json"

        save_data = {
            "game_info": self.game_info,
            "state": self.state.to_dict(),
            "timestamp": datetime.now().isoformat(),
            "version": self.game_info.get("version", "2.0")
        }

        with open(save_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)

        if self.debug:
            print(f"[DEBUG] Game saved to {save_file}")

        return str(save_file)

    def load_game(self, slot_name: str = "autosave") -> bool:
        """
        Load a game from a file.

        Args:
            slot_name: Name of the save slot

        Returns:
            True if successful, False otherwise
        """
        save_file = self.save_dir / f"{slot_name}.json"

        if not save_file.exists():
            return False

        with open(save_file, 'r', encoding='utf-8') as f:
            save_data = json.load(f)

        self.state = GameState.from_dict(save_data["state"])
        self._trigger_hooks("on_load", slot_name)

        if self.debug:
            print(f"[DEBUG] Game loaded from {save_file}")

        return True

    def list_saves(self) -> List[Dict[str, Any]]:
        """List all save files."""
        saves = []
        for save_file in self.save_dir.glob("*.json"):
            try:
                with open(save_file, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                saves.append({
                    "name": save_file.stem,
                    "timestamp": save_data.get("timestamp", "Unknown"),
                    "scene": save_data["state"]["current_scene"],
                    "version": save_data.get("version", "Unknown")
                })
            except Exception as e:
                if self.debug:
                    print(f"[DEBUG] Failed to read {save_file}: {e}")

        return sorted(saves, key=lambda x: x["timestamp"], reverse=True)

    def render_scene(self) -> Dict[str, Any]:
        """
        Render the current scene for display.

        Returns:
            Dictionary containing scene data and UI elements
        """
        scene = self.get_current_scene()
        if not scene:
            return {"error": "Scene not found"}

        return {
            "title": scene.title,
            "description": scene.description,
            "choices": [{"index": i, "text": c.text} for i, c in enumerate(self.get_available_choices())],
            "state": {
                "hp": self.state.hp,
                "morality": self.state.morality,
                "size": self.state.size,
                "knowledge": self.state.knowledge,
                "gold": self.state.gold,
                "inventory": self.state.inventory,
                "achievements": self.state.achievements,
                "stats": self.state.stats
            },
            "media": {
                "image_prompt": scene.image_prompt,
                "music": scene.music,
                "narrator": scene.narrator
            }
        }

    def get_ending(self) -> Optional[Dict]:
        """
        Determine which ending to show based on game state.

        Returns:
            Ending data or None
        """
        endings = self.script.get("endings", [])

        # Check for special endings with requirements
        for ending in endings:
            if ending.get("requirements"):
                if self._check_requirements(ending["requirements"]):
                    return ending

        # Default to morality-based endings
        morality = self.state.morality
        if morality >= 80:
            return next((e for e in endings if e.get("tier") == "perfect"), None)
        elif morality >= 60:
            return next((e for e in endings if e.get("tier") == "good"), None)
        elif morality >= 40:
            return next((e for e in endings if e.get("tier") == "neutral"), None)
        else:
            return next((e for e in endings if e.get("tier") == "bad"), None)

    def jump_to_scene(self, scene_id: str):
        """Jump directly to a scene (for debugging/testing)."""
        self.state.current_scene = scene_id

    def set_state(self, **kwargs):
        """Set specific state values (for debugging/testing)."""
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)


def load_script(script_path: str) -> Dict:
    """Load a game script from a JSON file."""
    with open(script_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_engine(script_path: str, save_dir: str = ".", debug: bool = False) -> TextAdventureEngine:
    """
    Convenience function to create a game engine from a script file.

    Args:
        script_path: Path to the game script JSON file
        save_dir: Directory for save files
        debug: Enable debug output

    Returns:
        Initialized TextAdventureEngine instance
    """
    script = load_script(script_path)
    return TextAdventureEngine(script, save_dir, debug)


if __name__ == "__main__":
    print("Text Adventure Game Engine v2.0")
    print("=" * 50)
    print("A flexible engine for creating interactive fiction.")
    print("\nUsage:")
    print("  engine = create_engine('game_script.json')")
    print("  scene = engine.render_scene()")
    print("  engine.make_choice(0)")
    print("  engine.save_game()")
