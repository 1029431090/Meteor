"""
    本程序是进行端点检测
    双门限法进行端点检测
"""
import numpy as np
import wave
from scipy.io import wavfile
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from pydub import AudioSegment
plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def STAc(x):
    """
    计算短时相关函数
    :param x:
    :return:
    """
    para = np.zeros(x.shape)
    fn = x.shape[1]
    for i in range(fn):
        R = np.correlate(x[:, i], x[:, i], 'valid')
        para[:, i] = R
    return para


def STEn(x, win, inc):
    """
    计算短时能量函数
    :param x:
    :param win:
    :param inc:
    :return:
    """
    X = enframe(x, win, inc)
    s = np.multiply(X, X)
    return np.sum(s, axis=1)


def STZcr(x, win, inc, delta=0):
    """
    计算短时过零率
    :param x:
    :param win:
    :param inc:
    :return:
    """
    absx = np.abs(x)
    x = np.where(absx < delta, 0, x)
    X = enframe(x, win, inc)
    X1 = X[:, :-1]
    X2 = X[:, 1:]
    s = np.multiply(X1, X2)
    sgn = np.where(s < 0, 1, 0)
    return np.sum(sgn, axis=1)


def FrameTimeC(frameNum, frameLen, inc, fs):
    ll = np.array([i for i in range(frameNum)])
    return ((ll - 1) * inc + frameLen / 2) / fs


def enframe(x, win, inc=None):
    nx = len(x)
    if isinstance(win, list) or isinstance(win, np.ndarray):
        nwin = len(win)
        nlen = nwin  # 帧长=窗长
    elif isinstance(win, int):
        nwin = 1
        nlen = win  # 设置为帧长
    if inc is None:
        inc = nlen
    nf = (nx - nlen + inc) // inc
    frameout = np.zeros((nf, nlen))
    indf = np.multiply(inc, np.array([i for i in range(nf)]))
    for i in range(nf):
        frameout[i, :] = x[indf[i]:indf[i] + nlen]
    if isinstance(win, list) or isinstance(win, np.ndarray):
        frameout = np.multiply(frameout, np.array(win))
    return frameout

def findSegment(express):
    """
    分割成語音段
    :param express:
    :return:
    """
    if express[0] == 0:
        voiceIndex = np.where(express)
    else:
        voiceIndex = express
    d_voice = np.where(np.diff(voiceIndex) > 1)[0]
    voiceseg = {}
    if len(d_voice) > 0:
        for i in range(len(d_voice) + 1):
            seg = {}
            if i == 0:
                st = voiceIndex[0]
                en = voiceIndex[d_voice[i]]
            elif i == len(d_voice):
                st = voiceIndex[d_voice[i - 1]+1]
                en = voiceIndex[-1]
            else:
                st = voiceIndex[d_voice[i - 1]+1]
                en = voiceIndex[d_voice[i]]
            seg['start'] = st
            seg['end'] = en
            seg['duration'] = en - st + 1
            voiceseg[i] = seg
    return voiceseg

def vad_TwoThr1(x, wlen, inc, NIS):
    """
    使用门限法检测语音段
    :param x: 语音信号
    :param wlen: 分帧长度
    :param inc: 帧移
    :param NIS:
    :return:
    """
    maxsilence = 15
    minlen = 5
    status = 0
    y = enframe(x, wlen, inc)
    fn = y.shape[0]
    amp = STEn(x, wlen, inc)
    ampth = np.mean(amp[:NIS])
    amp2 = 7.5 * ampth
    amp1 = 10 * ampth
    xn = 0
    count = np.zeros(fn)
    silence = np.zeros(fn)
    x1 = np.zeros(fn)
    x2 = np.zeros(fn)
    for n in range(fn):
        if status == 0 or status == 1:
            if amp[n] > amp1:
                x1[xn] = max(1, n - count[xn] - 1)
                status = 2
                silence[xn] = 0
                count[xn] += 1
            elif amp[n] > amp2 :
                status = 1
                count[xn] += 1
            else:
                status = 0
                count[xn] = 0
                x1[xn] = 0
                x2[xn] = 0

        elif status == 2:
            if amp[n] > amp2 :
                count[xn] += 1
            else:
                silence[xn] += 1
                if silence[xn] < maxsilence:
                    count[xn] += 1
                elif count[xn] < minlen:
                    status = 0
                    silence[xn] = 0
                    count[xn] = 0
                else:
                    status = 3
                    x2[xn] = x1[xn] + count[xn]
        elif status == 3:
            status = 0
            xn += 1
            count[xn] = 0
            silence[xn] = 0
            x1[xn] = 0
            x2[xn] = 0
    el = len(x1[:xn])
    if x1[el - 1] == 0:
        el -= 1
    if x2[el - 1] == 0:
        print('Error: Not find endding point!\n')
        x2[el] = fn
    SF = np.zeros(fn)
    NF = np.ones(fn)
    for i in range(el):
        SF[int(x1[i]):int(x2[i])] = 1
        NF[int(x1[i]):int(x2[i])] = 0
    voiceseg = findSegment(np.where(SF == 1)[0])
    vsl = len(voiceseg.keys())
    return voiceseg, vsl, SF, NF, amp



if __name__ == '__main__':

    wavepath = './vadtest/60_805.wav'
    f = wave.open(wavepath, 'rb')
    params = f.getparams()
    nchannels, sampwidth, fs, nframes = params[:4]  # 声道数、量化位数、采样频率、采样点数
    str_data = f.readframes(nframes)  # 读取音频，字符串格式
    f.close()
    wavedata = np.fromstring(str_data, dtype=np.short)  # 将字符串转化为浮点型数据
    data = wavedata * 1.0 / (max(abs(wavedata)))  # wave幅值归一化

    data /= np.max(data)
    N = len(data)
    wlen = 200
    inc = 80
    IS = 1
    overlap = wlen - inc
    NIS = int((IS * fs - wlen) // inc + 1)
    fn = (N - wlen) // inc + 1

    frameTime = FrameTimeC(fn, wlen, inc, fs)  # 计算出对应的时间
    time = [i / fs for i in range(N)]

    #voiceseg, vsl, SF, NF, amp, zcr = vad_TwoThr(data, wlen, inc, NIS)
    voiceseg, vsl, SF, NF, amp = vad_TwoThr1(data, wlen, inc, NIS)

    plt.subplot(2, 1, 1)
    plt.ylabel('幅值')
    plt.ylim((-1, 1))  # 设置y轴刻度范围为0~11
    plt.title('纯音频波形图')  # 设置绘图标题
    plt.plot(time, data)

    plt.subplot(2, 1, 2)
    plt.plot(frameTime, amp)
    plt.ylabel('幅值')
    plt.xlabel('时间(s)')  # 设置x、y轴标签
    plt.title('音频短时能量图')  # 设置绘图标题

    for i in range(vsl):
        plt.subplot(2, 1, 1)
        plt.vlines(frameTime[voiceseg[i]['start']],-1,1,colors='r',linestyles='dashed')
        plt.vlines(frameTime[voiceseg[i]['end']], -1, 1, colors='g', linestyles='dashed')
    plt.show()

