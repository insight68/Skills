"""
Rational Clarity - Apple Style Cards
Creating museum-quality comparison cards with extreme precision
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Canvas dimensions - Apple card ratio
WIDTH, HEIGHT = 1200, 1600

# Color palette - Apple inspired
BG_OFF_WHITE = (250, 250, 248)
BG_PURE_WHITE = (255, 255, 255)
TEXT_PRIMARY = (29, 29, 31)
TEXT_SECONDARY = (99, 99, 102)
TEXT_TERTIARY = (174, 174, 178)
ACCENT_BLUE = (0, 122, 255)
ACCENT_ORANGE = (255, 149, 0)
SUBTLE_GRAY = (242, 242, 247)
DIVIDER_LINE = (228, 228, 231)

def load_font(font_path, size):
    """Load font with fallback"""
    try:
        return ImageFont.truetype(font_path, size)
    except:
        return ImageFont.load_default()

def create_card_base():
    """Create the base card with Apple-style aesthetics"""
    # Create image with off-white background (Apple's favorite)
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_OFF_WHITE)
    draw = ImageDraw.Draw(img)

    # Add subtle inner shadow/glow effect at edges
    for i in range(3):
        alpha = 5 - i
        draw.rectangle([i, i, WIDTH-i, HEIGHT-i], outline=(220, 220, 222))

    return img, draw

def draw_horizontal_rule(draw, y, margin=80):
    """Draw a horizontal divider line"""
    draw.line([(margin, y), (WIDTH - margin, y)], fill=DIVIDER_LINE, width=1)

def create_title_section(draw, title, subtitle):
    """Create the title section with Apple typography"""
    # Load fonts
    font_title = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 48)
    font_subtitle = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 20)

    # Calculate text positioning
    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (WIDTH - title_width) // 2

    # Draw title
    draw.text((title_x, 120), title, fill=TEXT_PRIMARY, font=font_title)

    # Draw subtitle centered
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (WIDTH - subtitle_width) // 2

    draw.text((subtitle_x, 185), subtitle, fill=TEXT_SECONDARY, font=font_subtitle)

    # Draw divider below title
    draw_horizontal_rule(draw, 240)

def create_comparison_item(draw, y_pos, category, left_label, left_value, right_label, right_value):
    """Create a comparison row with two sides"""
    font_category = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 16)
    font_label = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 15)
    font_value = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 17)

    # Category label (small, centered, uppercase, widely spaced)
    category_text = category.upper()
    category_bbox = draw.textbbox((0, 0), category_text, font=font_category)
    category_width = category_bbox[2] - category_bbox[0]
    draw.text(((WIDTH - category_width) // 2, y_pos), category_text, fill=TEXT_TERTIARY, font=font_category)

    # Values below
    value_y = y_pos + 50

    # Left side - Skills
    left_label_bbox = draw.textbbox((0, 0), left_label, font=font_label)
    left_label_width = left_label_bbox[2] - left_label_bbox[0]
    draw.text(((WIDTH // 2 - left_label_width - 80), value_y), left_label, fill=TEXT_SECONDARY, font=font_label)

    left_value_bbox = draw.textbbox((0, 0), left_value, font=font_value)
    left_value_width = left_value_bbox[2] - left_value_bbox[0]
    draw.text(((WIDTH // 2 - left_value_width - 80), value_y + 30), left_value, fill=TEXT_PRIMARY, font=font_value)

    # Right side - n8n
    right_label_bbox = draw.textbbox((0, 0), right_label, font=font_label)
    draw.text(((WIDTH // 2 + 80), value_y), right_label, fill=TEXT_SECONDARY, font=font_label)

    right_value_bbox = draw.textbbox((0, 0), right_value, font=font_value)
    draw.text(((WIDTH // 2 + 80), value_y + 30), right_value, fill=TEXT_PRIMARY, font=font_value)

    # Vertical divider in center
    center_x = WIDTH // 2
    for i in range(-15, 16):
        alpha = 80 if abs(i) < 10 else 40
        draw.point((center_x, value_y + 10 + i), fill=DIVIDER_LINE)

    return value_y + 100

def create_card_1_scenarios():
    """Card 1: 适用场景"""
    img, draw = create_card_base()

    create_title_section(draw, "适用场景", "SCENARIOS")

    y_pos = 320
    y_pos = create_comparison_item(
        draw, y_pos,
        "任务类型",
        "Skills",
        "探索性任务",
        "n8n",
        "流程化事务"
    )

    # Add visual element - geometric shapes representing exploration vs flow
    circle_y = y_pos + 60
    # Left: scattered circles (exploration)
    for i in range(5):
        x_offset = 180 + i * 70
        y_offset = circle_y + (i % 3) * 20
        radius = 8 + (i % 3) * 4
        draw.ellipse([x_offset - radius, y_offset - radius, x_offset + radius, y_offset + radius],
                     outline=ACCENT_BLUE, width=2)

    # Right: connected flow (process)
    line_y = circle_y + 20
    for i in range(5):
        x = 720 + i * 70
        draw.ellipse([x - 8, line_y - 8, x + 8, line_y + 8], fill=ACCENT_ORANGE)
        if i < 4:
            draw.line([(x + 8, line_y), (x + 62, line_y)], fill=ACCENT_ORANGE, width=2)

    # Footer text
    font_footer = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 13)
    footer_text = "探索 vs 流程"
    footer_bbox = draw.textbbox((0, 0), footer_text, font=font_footer)
    draw.text(((WIDTH - footer_bbox[2]) // 2, HEIGHT - 80), footer_text, fill=TEXT_TERTIARY, font=font_footer)

    return img

def create_card_2_dependencies():
    """Card 2: 依赖关系"""
    img, draw = create_card_base()

    create_title_section(draw, "依赖关系", "DEPENDENCIES")

    y_pos = 320
    y_pos = create_comparison_item(
        draw, y_pos,
        "核心依赖",
        "Skills",
        "模型能力",
        "n8n",
        "工具集成"
    )

    # Visual representation
    vis_y = y_pos + 60

    # Left: Model representation (neural network nodes)
    centers = [(200, vis_y), (260, vis_y - 40), (260, vis_y + 40), (320, vis_y)]
    for cx, cy in centers:
        draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], outline=ACCENT_BLUE, width=2)
    # Connections
    draw.line([(200, vis_y), (260, vis_y - 40)], fill=ACCENT_BLUE, width=1)
    draw.line([(200, vis_y), (260, vis_y + 40)], fill=ACCENT_BLUE, width=1)
    draw.line([(260, vis_y - 40), (320, vis_y)], fill=ACCENT_BLUE, width=1)
    draw.line([(260, vis_y + 40), (320, vis_y)], fill=ACCENT_BLUE, width=1)

    # Right: Tools representation (modular blocks)
    block_y = vis_y - 30
    for i in range(3):
        bx = 700 + i * 80
        draw.rectangle([bx, block_y, bx + 50, block_y + 60], outline=ACCENT_ORANGE, width=2)
        draw.line([(bx + 50, block_y + 30), (bx + 80, block_y + 30)], fill=ACCENT_ORANGE, width=2)

    # Footer
    font_footer = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 13)
    footer_text = "智能 vs 连接"
    footer_bbox = draw.textbbox((0, 0), footer_text, font=font_footer)
    draw.text(((WIDTH - footer_bbox[2]) // 2, HEIGHT - 80), footer_text, fill=TEXT_TERTIARY, font=font_footer)

    return img

def create_card_3_skills():
    """Card 3: 技能要求"""
    img, draw = create_card_base()

    create_title_section(draw, "技能要求", "SKILL REQUIREMENTS")

    y_pos = 320
    y_pos = create_comparison_item(
        draw, y_pos,
        "所需能力",
        "Skills",
        "软件工程思维",
        "n8n",
        "节点配置理解"
    )

    # Visual: code brackets vs nodes
    vis_y = y_pos + 60

    # Left: Code representation
    font_mono = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/GeistMono-Regular.ttf', 24)
    draw.text((180, vis_y), "{  }", fill=ACCENT_BLUE, font=font_mono)
    font_small = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 14)
    draw.text((180, vis_y + 50), "logic.code()", fill=TEXT_SECONDARY, font=font_small)

    # Right: Node representation
    for i in range(3):
        nx = 700 + i * 90
        ny = vis_y + 15 + (i % 2) * 5
        draw.rounded_rectangle([nx, ny, nx + 60, ny + 35], radius=8, outline=ACCENT_ORANGE, width=2)

    # Footer
    font_footer = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 13)
    footer_text = "编程 vs 配置"
    footer_bbox = draw.textbbox((0, 0), footer_text, font=font_footer)
    draw.text(((WIDTH - footer_bbox[2]) // 2, HEIGHT - 80), footer_text, fill=TEXT_TERTIARY, font=font_footer)

    return img

def create_card_4_logic():
    """Card 4: 核心逻辑"""
    img, draw = create_card_base()

    create_title_section(draw, "核心逻辑", "CORE LOGIC")

    y_pos = 320
    y_pos = create_comparison_item(
        draw, y_pos,
        "SOP 实现",
        "Skills",
        "代码化",
        "n8n",
        "节点化"
    )

    # Visual transformation diagram
    vis_y = y_pos + 50

    # Left: SOP -> Code
    font_small = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 14)

    # SOP document icon
    draw.rectangle([160, vis_y, 200, vis_y + 60], outline=TEXT_TERTIARY, width=1)
    for i in range(3):
        draw.line([(165, vis_y + 15 + i * 15), (195, vis_y + 15 + i * 15)], fill=TEXT_TERTIARY, width=1)
    draw.text((155, vis_y + 70), "SOP", fill=TEXT_TERTIARY, font=font_small)

    # Arrow to code
    draw.polygon([(240, vis_y + 30), (255, vis_y + 25), (255, vis_y + 35)], fill=ACCENT_BLUE)

    # Code block
    draw.rectangle([270, vis_y - 5, 330, vis_y + 65], outline=ACCENT_BLUE, width=2)
    font_mono = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/GeistMono-Regular.ttf', 12)
    draw.text((280, vis_y + 10), "def", fill=ACCENT_BLUE, font=font_mono)
    draw.text((280, vis_y + 28), "sop():", fill=ACCENT_BLUE, font=font_mono)
    draw.text((282, vis_y + 46), "...", fill=TEXT_SECONDARY, font=font_mono)

    # Right: SOP -> Nodes
    # SOP document icon
    draw.rectangle([680, vis_y, 720, vis_y + 60], outline=TEXT_TERTIARY, width=1)
    for i in range(3):
        draw.line([(685, vis_y + 15 + i * 15), (715, vis_y + 15 + i * 15)], fill=TEXT_TERTIARY, width=1)
    draw.text((675, vis_y + 70), "SOP", fill=TEXT_TERTIARY, font=font_small)

    # Arrow to nodes
    draw.polygon([(760, vis_y + 30), (775, vis_y + 25), (775, vis_y + 35)], fill=ACCENT_ORANGE)

    # Node flow
    for i in range(3):
        nx = 800 + i * 75
        draw.rounded_rectangle([nx, vis_y + 10, nx + 55, vis_y + 50], radius=6, outline=ACCENT_ORANGE, width=2)
        if i < 2:
            draw.line([(nx + 55, vis_y + 30), (nx + 75, vis_y + 30)], fill=ACCENT_ORANGE, width=2)

    # Footer
    font_footer = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 13)
    footer_text = "编码 vs 节点"
    footer_bbox = draw.textbbox((0, 0), footer_text, font=font_footer)
    draw.text(((WIDTH - footer_bbox[2]) // 2, HEIGHT - 80), footer_text, fill=TEXT_TERTIARY, font=font_footer)

    return img

# Create all four cards
print("Creating Apple-style comparison cards...")
card1 = create_card_1_scenarios()
card1.save('/Users/chunjun/.claude/skills/canvas-design/card_1_scenarios.png')
print("✓ Card 1: Scenarios")

card2 = create_card_2_dependencies()
card2.save('/Users/chunjun/.claude/skills/canvas-design/card_2_dependencies.png')
print("✓ Card 2: Dependencies")

card3 = create_card_3_skills()
card3.save('/Users/chunjun/.claude/skills/canvas-design/card_3_skills.png')
print("✓ Card 3: Skills")

card4 = create_card_4_logic()
card4.save('/Users/chunjun/.claude/skills/canvas-design/card_4_logic.png')
print("✓ Card 4: Core Logic")

print("\n✨ All cards created with Rational Clarity philosophy")
print("Saved to: /Users/chunjun/.claude/skills/canvas-design/")
