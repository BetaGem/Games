# coding=utf-8
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.figure(figsize=(16,8))
plt.rcParams["font.size"] = 18
plt.subplots_adjust(hspace=0,wspace=0)

# 取不同的 r 值
for n,r in enumerate([.4,.7]):
    
    H = 2            # 点光源到液面的高度
    Nz = 200         # 竖向微元数量
    Nxy = 1200        # 角向微元数量
    
    # 设置面元
    Z = np.array([])
    Phi = np.arange(0, 2*np.pi, 2*np.pi/Nxy)
    for i in range(Nxy): 
        Z = np.hstack((Z, np.arange(0,1,1/Nz)))
    for i in range(Nz-1): 
        Phi = np.vstack((Phi, np.arange(0, 2*np.pi, 2*np.pi/Nxy)))
        
    Cylinder = pd.DataFrame(columns=["x","y","z","phi"]) 
    Cylinder["phi"] = Phi.T.reshape(Nz * Nxy,)
    Cylinder["z"] = Z + 0.5 / Nz
    Cylinder["x"] = r + np.cos(Cylinder["phi"])
    Cylinder["y"] = np.sin(Cylinder["phi"])
    
    # 初始化像平面
    pixel = 2e-3
    Base = np.zeros((int(4/pixel), int(4/pixel)))
    
    # 对每一个面元，求反射点位置与反射强度
    for i in range(len(Cylinder)):
        z, phi = Cylinder["z"][i], Cylinder["phi"][i]
        h = (H + 1) / z - 1
        # 反射点的坐标
        x = ((h - 1) * (r + np.cos(phi)) + r * (1 - np.cos(2*phi))) / h
        y = ((h - 1) * np.sin(phi) - r * np.sin(2*phi)) / h
        # 入射角和折射角
        i1 = np.arccos((1 + r * np.cos(phi)) / np.sqrt(1 + r**2 + (H-z)**2 + 2*r*np.cos(phi)))
        i2 = np.arcsin(np.sin(i1) / 1.5) # 取玻璃折射率为1.5
        # 考虑面源对光源的张角、反射率随入射角的变化（菲涅尔反射公式）
        flux = 1 / abs(((2*r**2 - h + 1 + r*(3-h) * np.cos(phi)) / z**2 / h**3))
        flux *= ((np.tan(i1-i2)/np.tan(i1+i2))**2 + (np.sin(i1-i2)/np.sin(i1+i2))**2) 
        
        Base[round(y/pixel + len(Base)/2)][round(x/pixel + len(Base[0])/2)] += flux
    
    # 画图
    plt.subplot(1,2,n+1)
    plt.imshow(np.cbrt(Base), cmap="pink")
    #plt.colorbar()
    plt.clim(0,8)
    plt.xticks([]);plt.yticks([])
    plt.text(100,1800,"$r=${:.1f}".format(r),c="w")
    
plt.savefig("./cylinder.jpg",dpi=500,bbox_inches='tight',pad_inches=0.)