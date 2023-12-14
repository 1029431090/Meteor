import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
import librosa.display


# Spectrogram步骤，
# Step 1: 预加重
# Step 2: 分帧
# Step 3: 加窗
# Step 4: FFT
# Step 5: 幅值平方
# Step 6: 对数功率
def preemphasis(signal, coeff=0.95):
    return np.append(signal[1], signal[1:] - coeff * signal[:-1])


def pow_spec(frames, NFFT):
    complex_spec = np.fft.rfft(frames, NFFT)
    return 1 / NFFT * np.square(np.abs(complex_spec))


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


if __name__ == '__main__':
    y, sr = sf.read(r'D:\Anaconda\code\数字信号处理\音频文件基本作图\文件\SDRSharp_20231026_084420Z_14659000Hz_AF.wav')
    # 预加重
    y = preemphasis(y, coeff=0.98)
    # 分帧加窗
    frames = frame_sig(y, frame_len=2048, frame_step=512, win_func=np.hanning)
    # FFT及幅值平方
    feature = pow_spec(frames, NFFT=2048)
    # 对数功率及绘图.
    librosa.display.specshow(librosa.power_to_db(feature.T), sr=sr, x_axis='time', y_axis='linear')
    plt.title('Spectrogram')
    plt.colorbar(format='%+2.0f dB')
    plt.tight_layout()
    plt.savefig(r'D:\Anaconda\code\数字信号处理\音频文件基本作图\文件\SDRSharp_20231026_084420Z_14659000Hz_AF.wav.png',
                dpi=1000)
    plt.show()
    plt.close()
