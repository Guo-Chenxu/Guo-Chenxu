import os
import urllib.request

def download_image(url, save_path):
    full_path = os.path.join(save_path, "acg.png")

    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0')

    with urllib.request.urlopen(req) as response, open(full_path, 'wb') as out_file:
        data = response.read()
        out_file.write(data)
    print(f"图片已成功下载至：{full_path}")
    # urllib.request.urlretrieve(url, full_path)
    # print(f"图片已成功下载至：{full_path}")

url = "https://www.loliapi.com/acg"
save_directory = "./img"

if not os.path.exists(save_directory):
    os.makedirs(save_directory)

download_image(url, save_directory)