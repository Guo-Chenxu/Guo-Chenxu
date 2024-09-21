import os
import urllib.request
import random
import shutil


def download_image(url, save_path):
    full_path = os.path.join(save_path, "acg.webp")

    req = urllib.request.Request(url)
    req.add_header(
        "User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    )

    with urllib.request.urlopen(req) as response, open(full_path, "wb") as out_file:
        data = response.read()
        out_file.write(data)
    print(f"图片已成功下载至：{full_path}")


# 似乎 github action 每次请求的图片都是同一张, 所以还是得用随机数
# url = f"https://www.loliapi.com/acg?id={random.randint(0, 999)}"
url = "https://www.loliapi.com/acg"
print(f"图片链接: {url}")
save_directory = "./acg-img"


if os.path.exists(save_directory):
    shutil.rmtree(save_directory)
os.makedirs(save_directory)

try:
    download_image(url, save_directory)
except Exception as e:
    print(f"下载图片时发生错误: {e}")
