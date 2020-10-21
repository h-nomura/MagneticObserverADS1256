import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import FastICA

#### signal generate ####
t = np.arange(0, 1, 0.001)

s1 = np.sin(2.0 * np.pi * 10 * t)
s2 = np.sin(2.0 * np.pi * 60 * t)
s3 = np.random.normal(loc=0, scale=1, size=len(t))
#### 3-signal print ####
fig = plt.figure(figsize=(20, 5))
ax1 = fig.add_subplot(1, 3, 1)
ax2 = fig.add_subplot(1, 3, 2)
ax3 = fig.add_subplot(1, 3, 3)
ax1.plot(t, s1, color="blue", label="Original signal 1 (s1)")
ax2.plot(t, s2, color="blue", label="Original signal 2 (s2)")
ax3.plot(t, s3, color="blue", label="Original signal 3 (s3)")
ax1.legend(loc = 'upper right') 
ax2.legend(loc = 'upper right') 
ax3.legend(loc = 'upper right') 
fig.tight_layout()
plt.show()
#### Linearly connect signals #####
y1 = 0.3 * s1 + 0.4 * s2 + 0.3 * s3
y2 = 0.4 * s1 + 0.1 * s2 + 0.5 * s3
y3 = 0.1 * s1 + 0.1 * s2 + 0.8 * s3
#### 3-signal print ####
fig = plt.figure(figsize=(20, 5))
ax1 = fig.add_subplot(1, 3, 1)
ax2 = fig.add_subplot(1, 3, 2)
ax3 = fig.add_subplot(1, 3, 3)
ax1.plot(t, y1, color="red",  label="Measurement signal 1 (y1)")
ax2.plot(t, y2, color="red", label="Measurement signal 2 (y2)")
ax3.plot(t, y3, color="red", label="Measurement signal 3 (y3)")
ax1.legend(loc = 'upper right') 
ax2.legend(loc = 'upper right') 
ax3.legend(loc = 'upper right') 
fig.tight_layout()
plt.show()
#### Perform ICA(independent component analysis) ####
Y = np.vstack([y1, y2, y3]).T

ica = FastICA(n_components=3, whiten=True)
ica.fit(Y)

X = ica.transform(Y)
x1 = np.array(X.T[0,:])
x2 = np.array(X.T[1,:])
x3 = np.array(X.T[2,:])

fig = plt.figure(figsize=(20, 5))
ax1 = fig.add_subplot(1, 3, 1)
ax2 = fig.add_subplot(1, 3, 2)
ax3 = fig.add_subplot(1, 3, 3)
ax1.plot(t, x1, color="green", label="Restored signal 1 (x1)")
ax2.plot(t, x2, color="green", label="Restored signal 2 (x2)")
ax3.plot(t, x3, color="green", label="Restored signal 3 (x3)")
ax1.legend(loc = 'upper right') 
ax2.legend(loc = 'upper right') 
ax3.legend(loc = 'upper right') 
fig.tight_layout()
plt.show()