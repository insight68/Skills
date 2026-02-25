#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text Adventure Game Player
A simple command-line interface to play text adventure games.
"""

import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.engine import create_engine


class GamePlayer:
    """Simple CLI player for text adventure games."""

    def __init__(self, script_path="scripts/example_game.json", save_dir="./saves"):
        """Initialize the game player."""
        self.engine = create_engine(script_path, save_dir=save_dir)
        self.running = True

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, text: str):
        """Print a formatted header."""
        print("\n" + "=" * 60)
        print(f"  {text}")
        print("=" * 60)

    def print_separator(self):
        """Print a visual separator."""
        print("-" * 60)

    def display_scene(self):
        """Display the current scene."""
        scene = self.engine.render_scene()

        # Clear screen for new scene
        self.clear_screen()

        # Title
        self.print_header(scene['title'])

        # Description
        print("\n" + scene['description'] + "\n")

        # Display stats if not on start/menu screens
        if scene['title'] not in ["🎮 The Beginning", "📖 How to Play", "🏆 Achievements"]:
            self.display_stats(scene['state'])

        # Display choices
        if scene['choices']:
            print("\n" + "➤ " * 20)
            print("\n  What do you do?\n")
            for i, choice in enumerate(scene['choices']):
                print(f"  [{i+1}] {choice['text']}")
            print("\n" + "➤ " * 20)

            # Special options
            print("\n  [S] Save Game  |  [L] Load Game  |  [Q] Quit")
        else:
            # End of game
            print("\n" + "=" * 60)
            print("  THE END")
            print("=" * 60)
            print("\n  [R] Play Again  |  [Q] Quit")

    def display_stats(self, state: dict):
        """Display player stats."""
        print("\n  ┌─ YOUR STATUS ─────────────────────────────┐")

        # Health bar
        hp = state['hp']
        hp_bar = "█" * (hp // 10) + "░" * (10 - hp // 10)
        print(f"  │  ❤️  Health:  [{hp_bar}] {hp}/100")

        # Morality bar
        morality = state['morality']
        morality_label = "💖 Heroic" if morality >= 70 else "⚖️ Neutral" if morality >= 40 else "😈 Dark"
        morality_bar = "█" * (morality // 10) + "░" * (10 - morality // 10)
        print(f"  │  {morality_label}: [{morality_bar}] {morality}/100")

        # Other stats
        if state.get('knowledge', 0) > 0:
            print(f"  │  🧠 Knowledge: {state['knowledge']}")
        if state.get('gold', 0) > 0:
            print(f"  │  💰 Gold: {state['gold']}")

        # Inventory
        if state['inventory']:
            items = ", ".join(state['inventory'][:3])
            if len(state['inventory']) > 3:
                items += f" (+{len(state['inventory']) - 3} more)"
            print(f"  │  🎒 Items: {items}")

        # Achievements
        if state['achievements']:
            print(f"  │  🏆 Achievements: {len(state['achievements'])}")

        print("  └──────────────────────────────────────────┘")

    def get_input(self) -> str:
        """Get and validate user input."""
        scene = self.engine.render_scene()
        num_choices = len(scene['choices'])

        while True:
            try:
                user_input = input("\n  Your choice: ").strip().upper()

                # Handle special commands
                if user_input in ['S', 'SAVE']:
                    return 'SAVE'
                elif user_input in ['L', 'LOAD']:
                    return 'LOAD'
                elif user_input in ['Q', 'QUIT']:
                    return 'QUIT'
                elif user_input in ['R', 'RESTART']:
                    return 'RESTART'
                elif user_input in ['H', 'HELP']:
                    return 'HELP'

                # Handle numeric choice
                choice_num = int(user_input)
                if 1 <= choice_num <= num_choices:
                    return str(choice_num - 1)  # Convert to 0-indexed
                else:
                    print(f"  ❌ Please enter a number between 1 and {num_choices}")
            except ValueError:
                print(f"  ❌ Invalid input. Please enter a number (1-{num_choices}) or S/L/Q/H")

    def handle_save(self):
        """Handle save game."""
        self.print_separator()
        slot_name = input("  Enter save slot name (or press Enter for 'autosave'): ").strip()
        if not slot_name:
            slot_name = "autosave"

        filepath = self.engine.save_game(slot_name)
        print(f"\n  ✅ Game saved to: {filepath}")
        input("\n  Press Enter to continue...")

    def handle_load(self):
        """Handle load game."""
        self.print_separator()
        saves = self.engine.list_saves()

        if not saves:
            print("\n  📭 No save files found.")
            input("\n  Press Enter to continue...")
            return

        print("\n  📂 Available Saves:\n")
        for i, save in enumerate(saves[:10], 1):
            print(f"  [{i}] {save['name']} - {save['scene']} ({save['timestamp']})")

        if len(saves) > 10:
            print(f"  ... and {len(saves) - 10} more")

        self.print_separator()
        choice = input("  Enter save number (or slot name): ").strip()

        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(saves):
                slot_name = saves[choice_num - 1]['name']
            else:
                print("  ❌ Invalid save number")
                input("\n  Press Enter to continue...")
                return
        except ValueError:
            slot_name = choice

        if self.engine.load_game(slot_name):
            print(f"\n  ✅ Game loaded from slot: {slot_name}")
        else:
            print(f"\n  ❌ Failed to load save: {slot_name}")

        input("\n  Press Enter to continue...")

    def show_help(self):
        """Show help information."""
        self.clear_screen()
        self.print_header("📖 HOW TO PLAY")

        print("""
  🎮 CONTROLS

  • Enter a NUMBER to select a choice
  • [S] Save your game progress
  • [L] Load a saved game
  • [H] Show this help screen
  • [Q] Quit the game

  📊 STATS

  • ❤️  Health - Your physical condition
  • 💖 Morality - Your moral alignment (affects ending!)
  • 🧠 Knowledge - Wisdom gained from exploration
  • 💰 Gold - Currency for special choices
  • 🎒 Items - Objects you've collected
  • 🏆 Achievements - Special accomplishments

  💡 TIPS

  • Your choices matter! Think carefully.
  • High morality = better endings
  • Explore everything for more knowledge
  • Save often to avoid losing progress
  • Some choices have hidden requirements
        """)

        input("\n  Press Enter to return to the game...")

    def run(self):
        """Main game loop."""
        # Show intro
        self.clear_screen()
        print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                        ║
    ║          ✨ THE ENCHANTED JOURNEY ✨                  ║
    ║                                                        ║
    ║              A Text Adventure Game                    ║
    ║                                                        ║
    ╚══════════════════════════════════════════════════════════╝
        """)

        input("  Press Enter to begin your adventure...")

        # Main game loop
        while self.running:
            self.display_scene()

            # Check for game over
            scene = self.engine.render_scene()
            if not scene['choices']:
                # End of game - wait for restart or quit
                while True:
                    cmd = self.get_input()
                    if cmd == 'RESTART':
                        # Restart game
                        self.__init__("scripts/example_game.json", save_dir="./saves")
                        break
                    elif cmd == 'QUIT':
                        self.running = False
                        break
                continue

            # Get and handle player input
            choice = self.get_input()

            if choice == 'QUIT':
                # Confirm quit
                confirm = input("\n  Are you sure you want to quit? (Y/N): ").strip().upper()
                if confirm == 'Y':
                    print("\n  Thanks for playing! 👋\n")
                    self.running = False
                continue

            elif choice == 'SAVE':
                self.handle_save()
                continue

            elif choice == 'LOAD':
                self.handle_load()
                continue

            elif choice == 'HELP':
                self.show_help()
                continue

            else:
                # Make the choice
                success = self.engine.make_choice(int(choice))
                if not success:
                    print("  ❌ Something went wrong. Please try again.")
                    input("\n  Press Enter to continue...")


def main():
    """Main entry point."""
    print("🎮 Loading game...")

    try:
        player = GamePlayer()
        player.run()
    except KeyboardInterrupt:
        print("\n\n  👋 Thanks for playing!")
    except Exception as e:
        print(f"\n\n  ❌ An error occurred: {e}")
        print("\n  If this persists, please report the issue.")
        input("\n  Press Enter to exit...")


if __name__ == "__main__":
    main()
