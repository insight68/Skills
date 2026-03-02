"""
投资如种地 - Apple Style Cards
基于 Temporal Agriculture 设计哲学
创建具有格调的对比卡片
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Canvas dimensions - Apple card ratio
WIDTH, HEIGHT = 1200, 1600

# Color palette - 大地色系 (Earth tones inspired by agriculture)
COLORS = {
    'cream': (250, 248, 242),           # 米白背景
    'soil_dark': (93, 64, 55),          # 深褐土壤
    'soil_light': (215, 204, 200),      # 浅褐土壤
    'seed_gold': (212, 165, 116),       # 种子金
    'sprout_green': (124, 179, 66),     # 嫩芽绿
    'harvest_orange': (255, 167, 38),   # 丰收橙
    'autumn_brown': (230, 81, 0),      # 秋天褐
    'winter_brown': (112, 68, 55),     # 冬天褐
    'spring_light': (139, 195, 74),    # 春天浅绿
    'sky_blue': (135, 206, 235),       # 天空蓝
    'pure_white': (255, 255, 255),     # 纯白
    'text_primary': (41, 41, 41),      # 主文字
    'text_secondary': (99, 99, 102),   # 次要文字
    'text_tertiary': (174, 174, 178),  # 三级文字
    'divider': (228, 228, 231),        # 分割线
}

def load_font(font_path, size):
    """Load font with fallback"""
    try:
        return ImageFont.truetype(font_path, size)
    except:
        return ImageFont.load_default()

def create_card_base():
    """Create the base card with warm agricultural aesthetics"""
    # Create image with cream background
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS['cream'])
    draw = ImageDraw.Draw(img)

    # Add subtle texture effect at edges
    for i in range(2):
        alpha = 3 - i
        draw.rectangle([i, i, WIDTH-i, HEIGHT-i], outline=(220, 218, 215))

    return img, draw

def draw_horizontal_rule(draw, y, margin=80, color=None):
    """Draw a horizontal divider line"""
    if color is None:
        color = COLORS['divider']
    draw.line([(margin, y), (WIDTH - margin, y)], fill=color, width=1)

def create_title_section(draw, title, subtitle, accent_color=None):
    """Create the title section"""
    font_title = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 52)
    font_subtitle = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 18)

    # Calculate text positioning
    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (WIDTH - title_width) // 2

    # Draw title
    draw.text((title_x, 100), title, fill=COLORS['text_primary'], font=font_title)

    # Draw subtitle centered
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (WIDTH - subtitle_width) // 2

    draw.text((subtitle_x, 170), subtitle, fill=COLORS['text_secondary'], font=font_subtitle)

    # Draw accent color bar below title
    if accent_color:
        bar_width = 200
        bar_x = (WIDTH - bar_width) // 2
        draw.rectangle([bar_x, 210, bar_x + bar_width, 215], fill=accent_color)

    # Draw divider
    draw_horizontal_rule(draw, 250)

def create_seasonal_bar(draw, y, colors):
    """Draw seasonal color bar"""
    bar_width = (WIDTH - 160) / len(colors)
    for i, color in enumerate(colors):
        draw.rectangle([80 + i * bar_width, y, 80 + (i + 1) * bar_width, y + 10], fill=color)

def create_card_1_time():
    """卡片1: 时间维度 - 季节轮回 vs 市场周期"""
    img, draw = create_card_base()

    # Seasonal color bar
    seasonal_colors = [COLORS['spring_light'], COLORS['harvest_orange'], COLORS['autumn_brown'], COLORS['winter_brown']]
    create_seasonal_bar(draw, HEIGHT - 1470, seasonal_colors)

    create_title_section(draw, "时间维度", "TEMPORAL RHYTHM", COLORS['seed_gold'])

    y_pos = 320

    # Left side - 农民的四季
    font_label = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 28)
    font_text = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 18)

    draw.text((100, y_pos), "农民的时间", fill=COLORS['text_primary'], font=font_label)

    seasons = [
        ("🌱 春季播种", COLORS['spring_light']),
        ("☀️ 夏季耕耘", COLORS['sprout_green']),
        ("🍂 秋季收获", COLORS['harvest_orange']),
        ("❄️ 冬季休养", COLORS['winter_brown'])
    ]

    for i, (text, color) in enumerate(seasons):
        y_item = y_pos + 60 + i * 55
        # Draw small circle icon
        draw.ellipse([120, y_item - 8, 136, y_item + 8], fill=color)
        draw.text((155, y_item - 9), text, fill=COLORS['text_secondary'], font=font_text)

    # Center spiral - growth pattern
    center_x, center_y = WIDTH // 2, y_pos + 140
    for i in range(8):
        radius = 6 + i * 5
        draw.ellipse([center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                     outline=COLORS['sprout_green'], width=2)

    # Right side - 投资者的周期
    draw.text((WIDTH // 2 + 100, y_pos), "投资者的周期", fill=COLORS['text_primary'], font=font_label)

    market_cycles = [
        ("📈 研究布局", COLORS['spring_light']),
        ("⏳ 持有等待", COLORS['sprout_green']),
        ("💰 收益兑现", COLORS['harvest_orange']),
        ("🔄 复盘调整", COLORS['winter_brown'])
    ]

    for i, (text, color) in enumerate(market_cycles):
        y_item = y_pos + 60 + i * 55
        draw.ellipse([WIDTH // 2 + 120, y_item - 8, WIDTH // 2 + 136, y_item + 8], fill=color)
        draw.text((WIDTH // 2 + 155, y_item - 9), text, fill=COLORS['text_secondary'], font=font_text)

    # Bottom wisdom
    y_bottom = 280
    font_wisdom = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 22)

    wisdom = "耐心等待时间发酵"
    wisdom_bbox = draw.textbbox((0, 0), wisdom, font=font_wisdom)
    draw.text(((WIDTH - wisdom_bbox[2]) // 2, y_bottom), wisdom, fill=COLORS['harvest_orange'], font=font_wisdom)

    font_quote = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 14)
    quote = '"好的投资就像好酒，需要时间来成熟"'
    quote_bbox = draw.textbbox((0, 0), quote, font=font_quote)
    draw.text(((WIDTH - quote_bbox[2]) // 2, y_bottom + 40), quote, fill=COLORS['text_secondary'], font=font_quote)

    # Decorative dots
    for i in range(7):
        draw.ellipse([WIDTH // 2 - 42 + i * 14, 180, WIDTH // 2 - 42 + i * 14 + 6, 186], fill=COLORS['seed_gold'])

    return img

def create_card_2_input():
    """卡片2: 投入维度 - 播种的勇气 vs 建仓的决心"""
    img, draw = create_card_base()

    # Seed gradient bar
    seed_colors = [COLORS['seed_gold']] * 20
    for i in range(20):
        alpha_factor = 1 - (i * 0.03)
        r = int(COLORS['seed_gold'][0] * alpha_factor)
        g = int(COLORS['seed_gold'][1] * alpha_factor)
        b = int(COLORS['seed_gold'][2] * alpha_factor)
        draw.rectangle([80 + i * (WIDTH - 160) // 20, HEIGHT - 1470,
                        80 + (i + 1) * (WIDTH - 160) // 20, HEIGHT - 1460], fill=(r, g, b))

    create_title_section(draw, "投入维度", "PLANTING DECISIONS", COLORS['seed_gold'])

    y_pos = 320
    font_label = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 28)
    font_text = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 18)

    # Left - 播种的智慧
    draw.text((100, y_pos), "播种的智慧", fill=COLORS['text_primary'], font=font_label)

    farming_steps = [
        "选择肥沃的土地",
        "深翻土壤做准备",
        "适时播种不抢早",
        "精心呵护幼苗",
        "除草防虫守护"
    ]

    for i, text in enumerate(farming_steps):
        y_item = y_pos + 60 + i * 55
        # Seed icon
        draw.ellipse([120, y_item - 6, 132, y_item + 6], fill=COLORS['seed_gold'])
        draw.text((150, y_item - 9), text, fill=COLORS['text_secondary'], font=font_text)

    # Center divider
    draw.line([(WIDTH // 2 - 1, y_pos + 40), (WIDTH // 2 + 1, y_pos + 320)],
              fill=COLORS['soil_light'], width=2)

    # Right - 建仓的策略
    draw.text((WIDTH // 2 + 100, y_pos), "建仓的策略", fill=COLORS['text_primary'], font=font_label)

    investment_steps = [
        "研究优质公司",
        "等待合理估值",
        "分批建仓不追高",
        "长期持有陪伴",
        "规避风险守护"
    ]

    for i, text in enumerate(investment_steps):
        y_item = y_pos + 60 + i * 55
        # Coin icon
        draw.ellipse([WIDTH // 2 + 120, y_item - 6, WIDTH // 2 + 132, y_item + 6], fill=COLORS['harvest_orange'])
        draw.text((WIDTH // 2 + 150, y_item - 9), text, fill=COLORS['text_secondary'], font=font_text)

    # Bottom
    y_bottom = 280
    font_wisdom = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 22)

    wisdom = "今日播种，明日收获"
    wisdom_bbox = draw.textbbox((0, 0), wisdom, font=font_wisdom)
    draw.text(((WIDTH - wisdom_bbox[2]) // 2, y_bottom), wisdom, fill=COLORS['harvest_orange'], font=font_wisdom)

    font_quote = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 14)
    quote = '"每一个伟大的投资，都始于一个勇敢的开始"'
    quote_bbox = draw.textbbox((0, 0), quote, font=font_quote)
    draw.text(((WIDTH - quote_bbox[2]) // 2, y_bottom + 40), quote, fill=COLORS['text_secondary'], font=font_quote)

    # Seed pattern
    for i in range(12):
        import math
        angle = i * 30
        x = WIDTH // 2 + 55 * math.cos(math.radians(angle))
        y = 160 + 55 * math.sin(math.radians(angle))
        draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=COLORS['seed_gold'])

    return img

def create_card_3_risk():
    """卡片3: 风险维度 - 自然灾害 vs 市场波动"""
    img, draw = create_card_base()

    # Warning color bar
    warning_colors = [COLORS['autumn_brown'], COLORS['winter_brown'], COLORS['autumn_brown'], COLORS['winter_brown']]
    create_seasonal_bar(draw, HEIGHT - 1470, warning_colors)

    create_title_section(draw, "风险维度", "WEATHERING STORMS", COLORS['autumn_brown'])

    y_pos = 320
    font_label = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 28)
    font_text = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 18)

    # Left - 自然风险
    draw.text((100, y_pos), "农民的风险", fill=COLORS['text_primary'], font=font_label)

    natural_risks = [
        ("🌪️ 暴风雨灾害", COLORS['autumn_brown']),
        ("🦗 虫害侵袭", COLORS['soil_dark']),
        ("🏜️ 干旱缺水", COLORS['harvest_orange']),
        ("❄️ 低温冻害", COLORS['winter_brown']),
        ("🔥 意外火灾", COLORS['text_primary'])
    ]

    for i, (text, color) in enumerate(natural_risks):
        y_item = y_pos + 60 + i * 50
        draw.text((130, y_item - 9), text, fill=COLORS['text_secondary'], font=font_text)

    # Protection
    font_small = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 16)
    draw.text((100, y_pos + 310), "防护：", fill=COLORS['autumn_brown'], font=font_small)
    protection = "灌溉系统 · 农药储备 · 保险覆盖"
    draw.text((145, y_pos + 310), protection, fill=COLORS['text_secondary'], font=font_small)

    # Center divider
    draw.line([(WIDTH // 2 - 1, y_pos + 30), (WIDTH // 2 + 1, y_pos + 340)],
              fill=COLORS['soil_light'], width=2)

    # Right - 市场波动
    draw.text((WIDTH // 2 + 100, y_pos), "市场的波动", fill=COLORS['text_primary'], font=font_label)

    market_risks = [
        ("📉 价格下跌", COLORS['autumn_brown']),
        ("📰 负面消息", COLORS['soil_dark']),
        ("🏛️ 政策变化", COLORS['harvest_orange']),
        ("💹 大盘调整", COLORS['winter_brown']),
        ("⚠️ 黑天鹅事件", COLORS['text_primary'])
    ]

    for i, (text, color) in enumerate(market_risks):
        y_item = y_pos + 60 + i * 50
        draw.text((WIDTH // 2 + 130, y_item - 9), text, fill=COLORS['text_secondary'], font=font_text)

    # Protection
    draw.text((WIDTH // 2 + 100, y_pos + 310), "防护：", fill=COLORS['autumn_brown'], font=font_small)
    protection = "分散投资 · 止损策略 · 长期视角"
    draw.text((WIDTH // 2 + 145, y_pos + 310), protection, fill=COLORS['text_secondary'], font=font_small)

    # Bottom
    y_bottom = 260
    font_wisdom = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 22)

    wisdom = "风雨过后是彩虹"
    wisdom_bbox = draw.textbbox((0, 0), wisdom, font=font_wisdom)
    draw.text(((WIDTH - wisdom_bbox[2]) // 2, y_bottom), wisdom, fill=COLORS['winter_brown'], font=font_wisdom)

    font_quote = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 14)
    quote = '"风险是成长的必经之路，承受得住波动才配得上收获"'
    quote_bbox = draw.textbbox((0, 0), quote, font=font_quote)
    draw.text(((WIDTH - quote_bbox[2]) // 2, y_bottom + 40), quote, fill=COLORS['text_secondary'], font=font_quote)

    # Raindrops decoration
    import random
    random.seed(42)
    for _ in range(25):
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, 180)
        draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=COLORS['sky_blue'])

    return img

def create_card_4_harvest():
    """卡片4: 收获维度 - 丰收的喜悦 vs 投资的回报"""
    img, draw = create_card_base()

    # Celebration color bar
    harvest_colors = [COLORS['harvest_orange'], COLORS['seed_gold'], COLORS['autumn_brown'], COLORS['harvest_orange']]
    create_seasonal_bar(draw, HEIGHT - 1470, harvest_colors)

    create_title_section(draw, "收获维度", "HARVEST SEASON", COLORS['harvest_orange'])

    y_pos = 320
    font_label = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 28)
    font_text = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 18)

    # Left - 农民的收获
    draw.text((100, y_pos), "农民的收获", fill=COLORS['text_primary'], font=font_label)

    harvests = [
        ("🌾 金黄麦浪", COLORS['harvest_orange']),
        ("🍎 硕果累累", COLORS['seed_gold']),
        ("🎉 丰收喜悦", COLORS['autumn_brown']),
        ("🏪 仓库充盈", COLORS['soil_dark']),
        ("💰 年成好收入", COLORS['text_primary'])
    ]

    for i, (text, color) in enumerate(harvests):
        y_item = y_pos + 60 + i * 50
        # Harvest icon
        draw.ellipse([120, y_item - 7, 134, y_item + 7], fill=color)
        draw.text((150, y_item - 9), text, fill=COLORS['text_secondary'], font=font_text)

    # Center abundance spiral
    center_x, center_y = WIDTH // 2, y_pos + 130
    for i in range(12):
        import math
        angle = i * 30
        radius = 25
        x = center_x + radius * math.cos(math.radians(angle))
        y = center_y + radius * math.sin(math.radians(angle))
        draw.ellipse([x - 5, y - 5, x + 5, y + 5], fill=COLORS['seed_gold'])

    # Right - 投资者的回报
    draw.text((WIDTH // 2 + 100, y_pos), "投资者的回报", fill=COLORS['text_primary'], font=font_label)

    returns = [
        ("📈 股价上涨", COLORS['harvest_orange']),
        ("💰 分红收益", COLORS['seed_gold']),
        ("🎯 目标达成", COLORS['autumn_brown']),
        ("📊 资产增值", COLORS['soil_dark']),
        ("✨ 财富自由", COLORS['text_primary'])
    ]

    for i, (text, color) in enumerate(returns):
        y_item = y_pos + 60 + i * 50
        draw.ellipse([WIDTH // 2 + 120, y_item - 7, WIDTH // 2 + 134, y_item + 7], fill=color)
        draw.text((WIDTH // 2 + 150, y_item - 9), text, fill=COLORS['text_secondary'], font=font_text)

    # Bottom
    y_bottom = 280
    font_wisdom = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 24)

    wisdom = "坚持终有回报"
    wisdom_bbox = draw.textbbox((0, 0), wisdom, font=font_wisdom)
    draw.text(((WIDTH - wisdom_bbox[2]) // 2, y_bottom), wisdom, fill=COLORS['harvest_orange'], font=font_wisdom)

    font_quote = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 14)
    quote = '"时间是好企业的朋友，是优秀投资者的试金石"'
    quote_bbox = draw.textbbox((0, 0), quote, font=font_quote)
    draw.text(((WIDTH - quote_bbox[2]) // 2, y_bottom + 40), quote, fill=COLORS['text_secondary'], font=font_quote)

    # Celebration ribbons
    import math
    for i in range(16):
        angle = i * 22.5
        length = 80 + (i % 3) * 15
        x1 = WIDTH // 2
        y1 = 140
        x2 = x1 + length * math.cos(math.radians(angle))
        y2 = y1 + length * math.sin(math.radians(angle))
        draw.line([(x1, y1), (x2, y2)], fill=COLORS['harvest_orange'], width=1)

    return img

def create_card_5_mindset():
    """卡片5: 心态维度 - 农夫的耐心 vs 投资者的定力"""
    img, draw = create_card_base()

    # Calm color bar
    calm_colors = [COLORS['winter_brown'], COLORS['soil_dark'], COLORS['sprout_green'], COLORS['sky_blue']]
    create_seasonal_bar(draw, HEIGHT - 1470, calm_colors)

    create_title_section(draw, "心态维度", "INNER PEACE", COLORS['sprout_green'])

    y_pos = 320
    font_label = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 28)
    font_text = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 18)

    # Left - 农夫的智慧
    draw.text((100, y_pos), "农夫的智慧", fill=COLORS['text_primary'], font=font_label)

    farmer_wisdom = [
        "⏳ 相信时间的力量",
        "🌱 不急躁，不强求",
        "🤲 勤劳不懒惰",
        "🙏 感恩天地馈赠",
        "🧘 顺应自然节奏"
    ]

    for i, text in enumerate(farmer_wisdom):
        y_item = y_pos + 60 + i * 50
        # Zen circle
        draw.ellipse([120, y_item - 8, 136, y_item + 8], outline=COLORS['sprout_green'], width=2)
        draw.text((150, y_item - 9), text, fill=COLORS['text_secondary'], font=font_text)

    # Center zen circle
    center_x, center_y = WIDTH // 2, y_pos + 140
    draw.ellipse([center_x - 45, center_y - 45, center_x + 45, center_y + 45],
                 outline=COLORS['soil_dark'], width=2)
    draw.ellipse([center_x - 30, center_y - 30, center_x + 30, center_y + 30], fill=COLORS['sprout_green'])
    draw.text((center_x - 8, center_y - 10), "静", fill=COLORS['cream'], font=font_label)

    # Right - 投资者的定力
    draw.text((WIDTH // 2 + 100, y_pos), "投资者的定力", fill=COLORS['text_primary'], font=font_label)

    investor_wisdom = [
        "💪 坚持长期主义",
        "🎯 不被短期波动",
        "📚 持续学习提升",
        "🤝 相信优秀团队",
        "🌟 保持初心不变"
    ]

    for i, text in enumerate(investor_wisdom):
        y_item = y_pos + 60 + i * 50
        # Stability icon
        draw.ellipse([WIDTH // 2 + 120, y_item - 8, WIDTH // 2 + 136, y_item + 8], fill=COLORS['seed_gold'])
        draw.text((WIDTH // 2 + 150, y_item - 9), text, fill=COLORS['text_secondary'], font=font_text)

    # Bottom
    y_bottom = 260
    font_wisdom = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 22)

    wisdom = "心静则明，定而生慧"
    wisdom_bbox = draw.textbbox((0, 0), wisdom, font=font_wisdom)
    draw.text(((WIDTH - wisdom_bbox[2]) // 2, y_bottom), wisdom, fill=COLORS['winter_brown'], font=font_wisdom)

    font_quote = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 14)
    quote = '"欲速则不达，见小利则大事不成"'
    quote_bbox = draw.textbbox((0, 0), quote, font=font_quote)
    draw.text(((WIDTH - quote_bbox[2]) // 2, y_bottom + 40), quote, fill=COLORS['text_secondary'], font=font_quote)

    # Peace doves
    draw.ellipse([80, 130, 140, 190], fill=COLORS['sky_blue'])
    draw.ellipse([WIDTH - 140, 130, WIDTH - 80, 190], fill=COLORS['sky_blue'])

    return img

def create_card_6_summary():
    """卡片6: 总结卡片 - 核心精髓"""
    img, draw = create_card_base()

    # Rainbow bar
    rainbow_colors = [COLORS['spring_light'], COLORS['sprout_green'], COLORS['harvest_orange'],
                       COLORS['autumn_brown'], COLORS['winter_brown'], COLORS['spring_light']]
    create_seasonal_bar(draw, HEIGHT - 1470, rainbow_colors)

    create_title_section(draw, "投资如种地", "INVESTMENT IS LIKE FARMING", COLORS['harvest_orange'])

    # Main concept circle
    center_x, center_y = WIDTH // 2, HEIGHT - 1100

    # Outer ring
    for i in range(16):
        import math
        angle = i * 22.5
        radius = 70
        x = center_x + radius * math.cos(math.radians(angle))
        y = center_y + radius * math.sin(math.radians(angle))
        draw.ellipse([x - 6, y - 6, x + 6, y + 6], fill=COLORS['seed_gold'])

    # Middle circle
    draw.ellipse([center_x - 45, center_y - 45, center_x + 45, center_y + 45], fill=COLORS['harvest_orange'])

    # Inner circle with text
    draw.ellipse([center_x - 28, center_y - 28, center_x + 28, center_y + 28], fill=COLORS['cream'])
    font_core = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 18)
    core_text = "耐心"
    core_bbox = draw.textbbox((0, 0), core_text, font=font_core)
    draw.text((center_x - core_bbox[2] // 2, center_y - core_bbox[3] // 2 - 8), core_text, fill=COLORS['text_primary'], font=font_core)

    # Four keywords
    keywords = [
        (100, center_y, "播种", COLORS['spring_light']),
        (WIDTH - 160, center_y, "收获", COLORS['harvest_orange']),
        (100, center_y - 180, "耕耘", COLORS['sprout_green']),
        (WIDTH - 160, center_y - 180, "守望", COLORS['winter_brown']),
    ]

    font_keyword = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 16)
    for x, y, word, color in keywords:
        draw.ellipse([x - 18, y - 18, x + 18, y + 18], fill=color)
        word_bbox = draw.textbbox((0, 0), word, font=font_keyword)
        draw.text((x - word_bbox[2] // 2, y - word_bbox[3] // 2 - 5), word, fill=COLORS['cream'], font=font_keyword)

    # Wisdom quotes
    y_bottom = HEIGHT - 1320
    font_wisdom = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 20)

    quotes = [
        "时间是最好的朋友",
        "耐心是最大的美德",
        "复利是奇迹的种子",
        "定力是成功的基石"
    ]

    for i, quote in enumerate(quotes):
        quote_bbox = draw.textbbox((0, 0), quote, font=font_wisdom)
        draw.text(((WIDTH - quote_bbox[2]) // 2, y_bottom - i * 35), quote, fill=COLORS['text_primary'], font=font_wisdom)

    # Final saying
    y_footer = 180
    font_final = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 24)

    final = "种瓜得瓜，种豆得豆"
    final_bbox = draw.textbbox((0, 0), final, font=font_final)
    draw.text(((WIDTH - final_bbox[2]) // 2, y_footer), final, fill=COLORS['harvest_orange'], font=font_final)

    font_english = load_font('/Users/chunjun/.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf', 14)
    english = '"You reap what you sow"'
    english_bbox = draw.textbbox((0, 0), english, font=english)
    draw.text(((WIDTH - english_bbox[2]) // 2, y_footer + 35), english, fill=COLORS['text_secondary'], font=font_english)

    # Growth lines radiating outward
    import math
    for i in range(40):
        angle = i * 9
        progress = i / 40
        radius_start = 110
        radius_end = 130 + progress * 25
        x1 = center_x + radius_start * math.cos(math.radians(angle))
        y1 = center_y + radius_start * math.sin(math.radians(angle))
        x2 = center_x + radius_end * math.cos(math.radians(angle))
        y2 = center_y + radius_end * math.sin(math.radians(angle))
        draw.line([(x1, y1), (x2, y2)], fill=COLORS['sprout_green'], width=1)

    return img

# Create all cards
print("创建「投资如种地」苹果风格卡片...")
print()

card1 = create_card_1_time()
card1.save('/Users/chunjun/.claude/skills/canvas-design/investment_farming_card_1_time.png')
print("✓ 卡片1: 时间维度")

card2 = create_card_2_input()
card2.save('/Users/chunjun/.claude/skills/canvas-design/investment_farming_card_2_input.png')
print("✓ 卡片2: 投入维度")

card3 = create_card_3_risk()
card3.save('/Users/chunjun/.claude/skills/canvas-design/investment_farming_card_3_risk.png')
print("✓ 卡片3: 风险维度")

card4 = create_card_4_harvest()
card4.save('/Users/chunjun/.claude/skills/canvas-design/investment_farming_card_4_harvest.png')
print("✓ 卡片4: 收获维度")

card5 = create_card_5_mindset()
card5.save('/Users/chunjun/.claude/skills/canvas-design/investment_farming_card_5_mindset.png')
print("✓ 卡片5: 心态维度")

card6 = create_card_6_summary()
card6.save('/Users/chunjun/.claude/skills/canvas-design/investment_farming_card_6_summary.png')
print("✓ 卡片6: 总结卡片")

print()
print("✨ 所有卡片基于「Temporal Agriculture」设计哲学创建完成")
print("📁 保存位置: /Users/chunjun/.claude/skills/canvas-design/")
