import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt
from pathlib import Path
import os


def get_spetrogram(wave_info):
    wave = np.array(wave_info, dtype="float")

    # 设置语谱图参数
    frame_len = 1000
    frame_off = frame_len // 2  # 非重叠点数
    specg_len = 2048

    # 可以想象1是代表第一帧，然后第二帧结尾超出第一帧frame_off个点，第三帧再超出第二帧frame_off个点，总共第二帧到最后一帧共有(wave.size - frame_len) // frame_off 帧
    frame_num = (wave.size - frame_len) // frame_off + 1
    # 生成汉明窗
    hamwindow = np.hamming(frame_len)
    specg = np.zeros((frame_num, specg_len // 2 + 1))
    z = np.zeros(specg_len - frame_len)

    for idx in range(frame_num):
        base = idx * frame_off
        frame = wave[base: base + frame_len]  # 分帧
        frame = np.append(frame * hamwindow, z)  # 加窗
        specg[idx:] = np.log10(np.abs(np.fft.rfft(frame)))  # FFT，返回幅度谱

    specg = np.transpose(specg)

    return specg


if __name__ == '__main__':
    origin_path = r'D:\Anaconda\code\数字信号处理\音频文件基本作图\文件'
    filename = r'flydog.web-sdr.net_2023-09-21T14_04_00Z_10221.00_usb.wav'
    if os.path.splitext(os.path.join(origin_path, filename))[-1] == '.wav':
        print(os.path.join(origin_path, filename))
        fs, x = wavfile.read(os.path.join(origin_path, filename))
        x_len = len(x)
        for i in range(1, 4):
            target_filename = os.path.join(origin_path, os.path.basename(filename) + '-' + str(i) + '.png')

            slice_x = x[(i - 1) * int(x_len / 3):i * int(x_len / 3)]
            spectro = get_spetrogram(slice_x)

            # 绘制图形
            plt.imshow(spectro, origin="lower", cmap="jet", aspect="auto", interpolation="none")
            plt.xticks([])
            plt.yticks([])
            plt.savefig(target_filename, dpi=1000)
            plt.close()
