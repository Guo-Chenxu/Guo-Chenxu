import os
import requests
import json
from PIL import Image, ImageDraw, ImageFont, ImageColor
from datetime import datetime, timedelta
import pathlib
import math

# 创建输出目录
pathlib.Path('stats-img').mkdir(exist_ok=True)

# 获取环境变量
USERNAME = os.environ.get('USERNAME') or 'Guo-Chenxu'
TOKEN = os.environ.get('GH_TOKEN')

headers = {}
if TOKEN:
    headers['Authorization'] = f'token {TOKEN}'


def fetch_user_stats():
    """获取用户GitHub统计数据"""
    url = f'https://api.github.com/users/{USERNAME}'
    user_response = requests.get(url, headers=headers)
    user_data = user_response.json()

    # 获取提交数据（最近一年）
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    year = today.year
    url = f'https://api.github.com/search/commits?q=author:{USERNAME}+author-date:>{one_year_ago.strftime("%Y-%m-%d")}'
    commits_response = requests.get(url, headers=headers)
    commits_count = 0
    try:
        commits_count = commits_response.json().get('total_count', 0)
    except:
        pass

    # 获取仓库数据
    url = f'https://api.github.com/users/{USERNAME}/repos'
    repos_response = requests.get(url, headers=headers)
    repos = repos_response.json()

    # 获取PR和Issues数据
    url = f'https://api.github.com/search/issues?q=author:{USERNAME}+type:pr'
    prs_response = requests.get(url, headers=headers)
    pr_count = prs_response.json().get('total_count', 0)

    url = f'https://api.github.com/search/issues?q=author:{USERNAME}+type:issue'
    issues_response = requests.get(url, headers=headers)
    issue_count = issues_response.json().get('total_count', 0)

    stars = sum(repo['stargazers_count'] for repo in repos if not repo['fork'])

    # 获取贡献的仓库数量
    contributed_to = 0
    for repo in repos:
        if repo['fork']:
            contributed_to += 1

    return {
        'Total Stars Earned': stars,
        f'Total Commits ({year})': commits_count,
        'Total PRs': pr_count,
        'Total Issues': issue_count,
        'Contributed to': contributed_to
    }


def fetch_user_languages():
    """获取用户使用的编程语言统计"""
    url = f'https://api.github.com/users/{USERNAME}/repos'
    response = requests.get(url, headers=headers)
    repos = response.json()

    languages = {}

    for repo in repos:
        if repo['fork']:
            continue

        lang_url = repo['languages_url']
        lang_response = requests.get(lang_url, headers=headers)
        lang_data = lang_response.json()

        for lang, bytes_count in lang_data.items():
            if lang in languages:
                languages[lang] += bytes_count
            else:
                languages[lang] = bytes_count

    # 按使用量排序并获取前6个
    total_bytes = sum(languages.values())
    sorted_languages = sorted(
        languages.items(), key=lambda x: x[1], reverse=True)[:6]

    # 转换为百分比
    result = {}
    for lang, bytes_count in sorted_languages:
        result[lang] = round((bytes_count / total_bytes) * 100, 2)

    return result


def generate_gradient_rectangle(width, height, start_color, end_color, horizontal=True):
    """生成渐变色背景"""
    rectangle = Image.new('RGBA', (width, height))
    draw = ImageDraw.Draw(rectangle)

    # 解析颜色
    r1, g1, b1 = ImageColor.getcolor(start_color, 'RGB')
    r2, g2, b2 = ImageColor.getcolor(end_color, 'RGB')

    if horizontal:
        for x in range(width):
            # 计算当前位置的颜色值
            r = int(r1 + (r2 - r1) * x / width)
            g = int(g1 + (g2 - g1) * x / width)
            b = int(b1 + (b2 - b1) * x / width)

            # 画垂直线
            draw.line([(x, 0), (x, height)], fill=(r, g, b))
    else:
        for y in range(height):
            # 计算当前位置的颜色值
            r = int(r1 + (r2 - r1) * y / height)
            g = int(g1 + (g2 - g1) * y / height)
            b = int(b1 + (b2 - b1) * y / height)

            # 画水平线
            draw.line([(0, y), (width, y)], fill=(r, g, b))

    return rectangle


def generate_language_image(languages):
    """生成语言统计图片"""
    width, height = 800, 400
    padding = 40
    bar_height = 30

    # 创建彩虹渐变背景
    img = generate_gradient_rectangle(width, height, "#52fa5a", "#c64dff")
    draw = ImageDraw.Draw(img)

    # 准备颜色
    colors = ['#ff5a36', '#ffbf36', '#51cc5a', '#36a3ff', '#9936ff', '#ff36bf']

    try:
        font = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 18)
    except:
        # 如果找不到字体，使用默认字体
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # 绘制语言条形图
    total_width = width - (padding * 2)
    bar_y = padding + 20

    # 绘制条形图
    x = padding
    for i, (lang, percentage) in enumerate(languages.items()):
        segment_width = int(total_width * percentage / 100)
        draw.rectangle([x, bar_y, x + segment_width, bar_y +
                       bar_height], fill=colors[i % len(colors)])
        x += segment_width

    # 绘制标签和百分比
    y_offset = bar_y + bar_height + 30
    col_width = width // 2
    row_height = 40

    for i, (lang, percentage) in enumerate(languages.items()):
        row = i // 2
        col = i % 2

        x = padding + (col * col_width)
        y = y_offset + (row * row_height)

        # 绘制颜色点
        draw.ellipse([x, y + 8, x + 16, y + 24], fill=colors[i % len(colors)])

        # 绘制语言名和百分比
        draw.text((x + 25, y), f"{lang} {percentage}%",
                  font=font_small, fill=(0, 0, 0))

    img.save('stats-img/github-langs.png', format='PNG')
    return True


def generate_stats_image(stats):
    """生成用户统计图片"""
    width, height = 800, 300
    padding = 40

    # 创建红到绿渐变背景
    img = generate_gradient_rectangle(width, height, "#ff5a36", "#52fa5a")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        # 如果找不到字体，使用默认字体
        font = ImageFont.load_default()

    icons = {
        'Total Stars Earned': "★",
        f'Total Commits ({datetime.now().year})': "↺",
        'Total PRs': "↯",
        'Total Issues': "!",
        'Contributed to': "☐"
    }

    # 绘制统计数据
    y_offset = padding + 20
    line_height = 45

    # 最高分数
    rating = "A+"

    # 绘制左侧数据
    for i, (title, value) in enumerate(stats.items()):
        y = y_offset + (i * line_height)
        draw.text(
            (padding, y), f"{icons.get(title, '')} {title}:", font=font, fill=(0, 0, 0))
        draw.text((width//2, y), str(value), font=font, fill=(0, 0, 0))

    # 绘制右侧评分圆环
    center_x = width - padding - 60
    center_y = height // 2
    radius = 50

    # 绘制圆环
    draw.ellipse([center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                 outline=(0, 0, 0), width=5)

    # 绘制评分文字
    draw.text((center_x - 20, center_y - 20),
              rating, font=font, fill=(0, 0, 0))

    img.save('stats-img/github-stats.png', format='PNG')
    return True


def main():
    print("Fetching GitHub statistics...")
    stats = fetch_user_stats()
    success = generate_stats_image(stats)
    if success:
        print("GitHub stats image generated successfully!")

    print("Fetching language statistics...")
    languages = fetch_user_languages()
    success = generate_language_image(languages)
    if success:
        print("Language stats image generated successfully!")


if __name__ == "__main__":
    main()
