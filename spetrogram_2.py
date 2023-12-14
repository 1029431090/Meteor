import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt

Fs, x = wavfile.read(
    r'D:\Anaconda\code\数字信号处理\音频文件基本作图\文件\flydog.web-sdr.net_2023-09-21T14_04_00Z_10221.00_usb.wav')
wave = np.array(x, dtype="float")

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

# aspect设为auto即可自动拉宽图
plt.imshow(specg, origin="lower", cmap="jet", aspect="auto", interpolation="none")
plt.xticks([])
plt.yticks([])
plt.savefig(
    r'D:\Anaconda\code\数字信号处理\音频文件基本作图\文件\flydog.web-sdr.net_2023-09-21T14_04_00Z_10221.00_usb.wav.png',
    dpi=1000)
# plt.show()
plt.close()
