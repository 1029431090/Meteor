from scipy import io
from scipy.io import wavfile
import matplotlib.pyplot as plt

Fs, x = wavfile.read(
    'D:\Anaconda\code\数字信号处理\音频文件基本作图\文件\SDRSharp_20231026_084420Z_14659000Hz_AF.wav')  # 读取音频
specg = plt.specgram(x, Fs=Fs, pad_to=256, NFFT=1024, noverlap=128)  # 提取语谱图，一键操作！
plt.savefig('D:\Anaconda\code\数字信号处理\音频文件基本作图\文件\SDRSharp_20231026_084420Z_14659000Hz_AF.wav.png',
            dpi=1000)
# io.savemat('specgram.mat', {'specg': specg[0]})  # 保存语谱图
# # 照例解释下参数
# x，Fs和上边一样
# pad_to为上边的nfft
# NFFT为上边的windows_length（为什么nfft不设置为上边的nfft呢，迷惑）
# noverlap为上边的overlap_length
