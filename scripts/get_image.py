import os
import time
import urllib.request
import random
import shutil


def download_image(url, save_path, filename="acg.webp"):
    print(f"图片链接: {url}")
    full_path = os.path.join(save_path, filename)

    req = urllib.request.Request(url, headers={
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    })

    with urllib.request.urlopen(req) as response, open(full_path, "wb") as out_file:
        data = response.read()
        out_file.write(data)
    print(f"图片已成功下载至：{full_path}")


def copy_random_image(src_dir, dest_dir, dest_filename):
    files = os.listdir(src_dir)
    images = [file for file in files if os.path.isfile(
        os.path.join(src_dir, file))]

    if not images:
        print("源目录中没有找到任何图片文件！")
        return

    selected_image = random.choice(images)
    src_path = os.path.join(src_dir, selected_image)
    dest_path = os.path.join(dest_dir, dest_filename)
    shutil.copy2(src_path, dest_path)

    print(f"已将图片 {selected_image} 复制并重命名为 {dest_filename}")


url = "https://www.loliapi.com/acg/pc/"
# url = "https://img.loliapi.cn/i/pc/img{}.webp"
save_directory = "./acg-img"
fallback_directory = "./acg-img-fallback"


if os.path.exists(save_directory):
    shutil.rmtree(save_directory)
os.makedirs(save_directory)

try:
    download_image(url, save_directory, "acg.webp")
except Exception as e:
    print(f"下载图片时发生错误: {e}")
    copy_random_image(fallback_directory, save_directory, "acg.webp")
