import os
import requests
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import json
from PIL import Image, ImageDraw, ImageFont
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

# 颜色方案
STATS_GRADIENT = ['#ea6161', '#ffc64d', '#fffc4d', '#52fa5a']
LANGS_GRADIENT = ['#52fa5a', '#4dfcff', '#c64dff']


def fetch_user_stats():
    """获取用户GitHub统计数据"""
    url = f'https://api.github.com/users/{USERNAME}'
    user_response = requests.get(url, headers=headers)
    user_data = user_response.json()

    # 获取提交数据（最近一年）
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
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

    stars = sum(repo['stargazers_count'] for repo in repos if not repo['fork'])
    forks = sum(repo['forks_count'] for repo in repos if not repo['fork'])

    return {
        'public_repos': user_data.get('public_repos', 0),
        'followers': user_data.get('followers', 0),
        'commits': commits_count,
        'stars': stars,
        'forks': forks,
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

    # 按使用量排序
    languages = dict(
        sorted(languages.items(), key=lambda x: x[1], reverse=True)[:6])

    total = sum(languages.values())

    # 转换为百分比
    for lang in languages:
        languages[lang] = (languages[lang] / total) * 100

    return languages


def generate_stats_image(stats):
    """生成用户统计图片"""
    fig, ax = plt.subplots(figsize=(8, 3.5))

    # 设置背景色渐变
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    plt.title(f"{USERNAME}'s GitHub Statistics",
              fontsize=16, fontweight='bold')

    # 绘制数据
    y_pos = np.arange(len(stats))
    ax.barh(y_pos, list(stats.values()), color=STATS_GRADIENT)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(list(stats.keys()))
    ax.invert_yaxis()  # 从上到下显示项目

    # 添加数值标签
    for i, v in enumerate(stats.values()):
        ax.text(v + 3, i, str(v), color='black', va='center')

    plt.tight_layout()
    plt.savefig('stats-img/github-stats.png', transparent=False, dpi=100)
    plt.close()


def generate_languages_image(languages):
    """生成语言统计图片"""
    fig, ax = plt.subplots(figsize=(8, 3.5))

    labels = languages.keys()
    sizes = languages.values()

    plt.title(f"{USERNAME}'s Most Used Languages",
              fontsize=16, fontweight='bold')

    patches, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.1f%%',
                                       startangle=90, colors=LANGS_GRADIENT)

    # 添加图例
    ax.legend(patches, labels, loc="center right", bbox_to_anchor=(1.1, 0.5))
    ax.axis('equal')  # 使饼图为正圆形

    plt.tight_layout()
    plt.savefig('stats-img/github-langs.png', transparent=False, dpi=100)
    plt.close()


def main():
    print("Fetching GitHub statistics...")
    stats = fetch_user_stats()
    generate_stats_image(stats)

    print("Fetching language statistics...")
    languages = fetch_user_languages()
    generate_languages_image(languages)

    print("Statistics images generated successfully!")


if __name__ == "__main__":
    main()
