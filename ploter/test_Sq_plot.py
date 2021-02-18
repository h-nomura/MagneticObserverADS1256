import math
import numpy as np
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(6,4))
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)

pi = math.pi   #mathモジュールのπを利用

x = np.linspace(0, 2*pi, 100)  #0から2πまでの範囲を100分割したnumpy配列
y = np.sin(x)

ax1.text(0.05, 0.8, "Python", size=15, transform= ax1.transAxes)
ax1.axhline(0.7, ls = "-.", color = "magenta")
ax1.plot(x, y)
ax2.axhline(0.3, ls = "-.", color = "magenta")
ax2.plot(x, y)
plt.show()