#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《尼尔斯骑鹅旅行记》游戏启动器
"""

import sys
import os

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from game_engine import GameEngine, load_script_from_file


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def print_state(state):
    """打印游戏状态"""
    print(f"❤️ 生命值: {state['hp']}")
    print(f"💖 道德值: {state['morality']}")
    print(f"📏 大小值: {state['size']}")
    print(f"📚 知识值: {state['knowledge']}")
    if state['inventory']:
        print(f"🎒 物品: {', '.join(state['inventory'])}")
    if state['achievements']:
        print(f"🏆 成就: {', '.join(state['achievements'])}")
    print()


def main():
    """主游戏循环"""
    # 加载游戏脚本
    script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'game_script.json')

    try:
        script_data = load_script_from_file(script_path)
    except FileNotFoundError:
        print(f"错误: 找不到游戏脚本文件 {script_path}")
        return
    except json.JSONDecodeError as e:
        print(f"错误: 游戏剧本格式错误 - {e}")
        return

    # 创建游戏引擎
    engine = GameEngine(script_data, save_dir="./saves")

    # 显示游戏标题
    game_info = script_data.get("game_info", {})
    print_header(game_info.get("title", "《尼尔斯骑鹅旅行记》"))
    print(game_info.get("description", ""))
    print()

    # 游戏主循环
    while True:
        # 渲染当前场景
        scene_data = engine.render_scene()

        if "error" in scene_data:
            print(f"错误: {scene_data['error']}")
            break

        # 检查是否是结局场景
        if engine.state.current_scene == "game_over":
            print_header("游戏结束")
            print("你的旅程结束了...")
            print_state(scene_data['state'])
            break

        # 检查是否达成结局
        ending = engine.get_ending()
        if engine.state.current_scene in ["ending_good", "ending_neutral", "ending_bad"]:
            print_header(f"🎬 {ending['title']}")
            print(ending['description'])
            print()
            print("最终状态:")
            print_state(scene_data['state'])
            print("\n感谢游玩！")
            break

        # 显示场景
        print_header(f"📍 {scene_data['title']}")
        print(scene_data['description'])
        print()

        # 显示状态
        print_state(scene_data['state'])

        # 显示选项
        choices = scene_data['choices']
        if not choices:
            print("没有可用选项，游戏结束。")
            break

        print("你的选择:")
        for choice in choices:
            print(f"  [{choice['index']}] {choice['text']}")

        # 获取玩家输入
        while True:
            try:
                user_input = input("\n请输入选项编号 (或输入 'q' 退出, 's' 保存): ").strip()

                if user_input.lower() == 'q':
                    print("感谢游玩！")
                    return
                elif user_input.lower() == 's':
                    save_file = engine.save_game()
                    print(f"✓ 游戏已保存到: {save_file}")
                    continue

                choice_index = int(user_input)
                if 0 <= choice_index < len(choices):
                    break
                else:
                    print(f"请输入 0-{len(choices)-1} 之间的数字")
            except ValueError:
                print("请输入有效的数字")
            except KeyboardInterrupt:
                print("\n\n感谢游玩！")
                return

        # 执行选择
        engine.make_choice(choice_index)

        # 自动保存
        engine.save_game("autosave")


if __name__ == "__main__":
    import json
    main()
