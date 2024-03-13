import os
import subprocess
import json
import numpy as np
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor, as_completed
counter = 0

# 函数：使用exiftool获取指定文件的EXIF信息
def get_exif_data(filepath):
    try:
        process = subprocess.Popen(['exiftool', '-FocalLength', '-json', filepath], stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        out, _ = process.communicate()
        exif_data = json.loads(out.decode('latin1'))[0]
        focal_length_str = exif_data.get('FocalLength', '')
        if focal_length_str:
            global counter
            counter += 1
            focal_length = float(focal_length_str.split()[0])
            print(counter, focal_length)
            return focal_length
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError):
        return None


# 函数：并行收集文件夹中所有文件的焦距信息
def collect_focal_lengths_parallel(root_folder):
    focal_lengths = []
    # 收集所有合适的文件路径
    file_paths = []
    for root, _, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith(('.jpg', '.raf', '.cr3', '.cr2', '.nef', '.arw', '.rw2', '.per', '.dng')):
                file_paths.append(os.path.join(root, file))

    # 使用ThreadPoolExecutor并行处理文件
    with ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(get_exif_data, filepath): filepath for filepath in file_paths}
        for future in as_completed(future_to_file):
            focal_length = future.result()
            if focal_length:
                focal_lengths.append(focal_length)

    return focal_lengths


# 函数：绘制焦距分布直方图
def plot_focal_length_distribution(focal_lengths):
    bins = np.arange(0, max(focal_lengths) + 10, 10)  # 设置直方图的分隔值
    plt.hist(focal_lengths, bins=bins, edgecolor="black")
    plt.xlabel('Focal Length (mm)')
    plt.ylabel('Number of Photos')
    plt.title('Focal Length Distribution')
    plt.xticks(bins)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()
    plt.savefig('output.jpg')


# 主程序
def main():
    root_folder = "C:/Users/MJ0530/Pictures/清华摄影队投稿"  # 请根据实际情况修改路径
    print("当前路径为", root_folder)

    focal_lengths = collect_focal_lengths_parallel(root_folder)

    if focal_lengths:
        plot_focal_length_distribution(focal_lengths)
    else:
        print('没有找到任何焦距信息')


if __name__ == '__main__':
    main()