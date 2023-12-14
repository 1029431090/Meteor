import os
import soundfile as sf
import numpy as np
import librosa.display
import matplotlib.pyplot as plt


# Spectrogram步骤，
# Step 1: 预加重
# Step 2: 分帧
# Step 3: 加窗
# Step 4: FFT
# Step 5: 幅值平方
# Step 6: 对数功率
def preemphasis(signal, coeff=0.95):
    return np.append(signal[1], signal[1:] - coeff * signal[:-1])


def frame_sig(sig, frame_len, frame_step, win_func):
    '''
    :param sig: 输入的语音信号
    :param frame_len: 帧长
    :param frame_step: 帧移
    :param win_func: 窗函数
    :return: array of frames, num_frame * frame_len
    '''
    slen = len(sig)

    if slen <= frame_len:
        num_frames = 1
    else:
        # np.ceil(), 向上取整
        num_frames = 1 + int(np.ceil((slen - frame_len) / frame_step))

    padlen = int((num_frames - 1) * frame_step + frame_len)
    # 将信号补长，使得(slen - frame_len) /frame_step整除
    zeros = np.zeros((padlen - slen,))
    padSig = np.concatenate((sig, zeros))

    indices = np.tile(np.arange(0, frame_len), (num_frames, 1)) + np.tile(
        np.arange(0, num_frames * frame_step, frame_step), (frame_len, 1)).T
    indices = np.array(indices, dtype=np.int32)
    frames = padSig[indices]
    win = np.tile(win_func(frame_len), (num_frames, 1))
    return frames * win


def pow_spec(frames, NFFT):
    complex_spec = np.fft.rfft(frames, NFFT)
    return 1 / NFFT * np.square(np.abs(complex_spec))


if __name__ == '__main__':
    origin_path = r'D:\Anaconda\code\数字信号处理\音频文件基本作图\文件'
    filename = r'flydog.web-sdr.net_2023-09-21T14_04_00Z_10221.00_usb.wav'

    # matplotlib设置中文字符
    plt.rcParams['font.sans-serif'] = ['SimHei']

    if os.path.splitext(os.path.join(origin_path, filename))[-1] == '.wav':
        print(os.path.join(origin_path, filename))
        x, fs = sf.read(os.path.join(origin_path, filename))
        x_len = len(x)
        for i in range(1, 4):
            change_filename = os.path.basename(filename) + '-' + str(i) + '.png'
            target_filename = os.path.join(origin_path, change_filename)

            slice_x = x[(i - 1) * int(x_len / 3):i * int(x_len / 3)]

            # 预加重
            y = preemphasis(slice_x, coeff=0.98)
            # 分帧加窗
            frames = frame_sig(y, frame_len=2048, frame_step=512, win_func=np.hamming)
            # FFT及幅值平方
            feature = pow_spec(frames, NFFT=2048)
            # 对数功率及绘图
            librosa.display.specshow(librosa.power_to_db(feature.T), sr=fs, x_axis='time', y_axis='linear')
            plt.title(f'{change_filename} 的语谱图')
            plt.colorbar(format='%+2.0f dB')
            plt.tight_layout()
            plt.savefig(target_filename, dpi=1200)
            plt.close()
