import numpy as np
import matplotlib.pyplot as plt


# 簡単な信号の作成
N = 128 # サンプル数
dt = 0.01 # サンプリング周期(sec):100ms =>サンプリング周波数100Hz
freq = 10 # 周波数(10Hz) =>正弦波の周期0.1sec
amp = 1 # 振幅
t = np.arange(0, N*dt, dt) # 時間軸
f = amp * np.sin(2*np.pi*freq*t) + 100 # 信号（周波数10、振幅1の正弦波）

# 高速フーリエ変換(FFT)
F = np.fft.fft(f) #

# FFTの複素数結果を絶対に変換
F_abs = np.abs(F)
# 振幅をもとの信号に揃える
F_abs_amp = F_abs / N * 2 # 交流成分はデータ数で割って2倍
F_abs_amp[0] = F_abs_amp[0] / 2 # 直流成分（今回は扱わないけど）は2倍不要

# 周波数軸のデータ作成
fq = np.linspace(0, 1.0/dt, N) # 周波数軸　linspace(開始,終了,分割数)

# グラフ表示
fig = plt.figure(figsize=(12, 4))
# 信号のグラフ（時間軸）
ax2 = fig.add_subplot(121)
plt.xlabel('time(sec)', fontsize=14)
plt.ylabel('amplitude', fontsize=14)
plt.plot(t, f)

# FFTのグラフ（周波数軸）
ax2 = fig.add_subplot(122)
plt.xlabel('freqency(Hz)', fontsize=14)
plt.ylabel('amplitude', fontsize=14)
plt.plot(fq[:int(N/2)+1], F_abs_amp[:int(N/2)+1]) # ナイキスト定数まで表示

plt.show()