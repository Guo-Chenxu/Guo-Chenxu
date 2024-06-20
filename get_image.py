import os
import urllib.request

def download_image(url, save_path):
    full_path = os.path.join(save_path, "acg.png")

    try:
        urllib.request.urlretrieve(url, full_path)
        print(f"图片已成功下载至：{full_path}")
    except urllib.error.URLError as e:
        print(f"下载图片时发生错误: {e.reason}")

url = "https://www.loliapi.com/acg"
save_directory = ".\img"

if not os.path.exists(save_directory):
    os.makedirs(save_directory)

download_image(url, save_directory)