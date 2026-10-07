import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Songti SC', 'Hiragino Sans GB', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

DEG2RAD = np.pi / 180.0 


# --- 步骤 1: 大气与散射物理常数 ---------------------------------------------
R_EARTH    = 6371e3            # 地球半径 [m]
R_ATMO     = R_EARTH + 100e3   # 大气顶半径 [m] (取大气厚度 100 km)
H_RAYLEIGH = 8.0e3             # Rayleigh 密度标高 [m]
H_MIE      = 1.2e3             # Mie 密度标高 [m]
BETA_R  = np.array([5.8e-6, 13.5e-6, 33.1e-6])   # 海平面 Rayleigh 系数 RGB [1/m]
BETA_M0 = 21e-6                # 海平面 Mie 系数 (参考 T=5) [1/m]
G_MIE   = 0.76                 # Mie 前向散射不对称因子


# --- 步骤 2: 相函数与几何 ---------------------------------------------------
def phase_rayleigh(costheta):
    """Rayleigh 相函数 P_R(θ)"""
    return 3.0 / (16.0 * np.pi) * (1.0 + costheta ** 2)

def phase_mie(costheta):
    """Mie 相函数 (Henyey-Greenstein, 前向散射)"""
    return (1 - G_MIE ** 2) / (4 * np.pi * (1 + G_MIE ** 2 - 2 * G_MIE * costheta) ** 1.5)

def dir_from_altaz(alt_deg, az_deg):
    """地平坐标 (高度 alt, 方位 az) -> 单位方向矢量; 本地坐标 x=东, y=北, z=天顶"""
    a, z = np.asarray(alt_deg) * DEG2RAD, np.asarray(az_deg) * DEG2RAD
    return np.stack([np.cos(a) * np.sin(z),
                     np.cos(a) * np.cos(z),
                     np.sin(a)], axis=-1)


# --- 步骤 3: 单次散射积分核 -------------------------------------------------
def single_scattering(omega, sun, beta_m, n_view=48, n_sun=24):
    """
    单次散射相对辐射亮度。
      omega  : (H,W,3) 每个天空方向的单位矢量
      sun    : (3,)    太阳方向单位矢量
      beta_m : 气溶胶 Mie 散射系数 [1/m]
      n_view : 沿视线的采样步数
      n_sun  : 沿太阳方向的采样步数
    返回 L : (H,W,3)  RGB 相对辐射亮度
    """
    H, W = omega.shape[:2]
    obs = np.array([0.0, 0.0, R_EARTH])           # 观测者 (海平面, z=天顶)

    # (a) 视线与地球/大气顶的交点距离, 得到积分上限 s_max
    b = R_EARTH * omega[..., 2]
    s_earth = np.where(b < 0, -2.0 * b, np.inf)
    disc = b * b - (R_EARTH ** 2 - R_ATMO ** 2)
    s_atmo = -b + np.sqrt(np.clip(disc, 0.0, None))
    s_max = np.minimum(s_atmo, s_earth)
    ds = s_max / n_view

    # (b) 散射角余弦 (太阳为平行光, 整条视线相同) 与相函数
    costheta = np.sum(omega * sun, axis=-1)
    P_R, P_M = phase_rayleigh(costheta), phase_mie(costheta)

    tau_view = np.zeros((H, W, 3))                # 视线方向消光累积
    L = np.zeros((H, W, 3))

    # (c) 沿视线积分
    for i in range(n_view):
        s = (i + 0.5) * ds                        # 中点采样
        p = obs + s[..., None] * omega
        r = np.linalg.norm(p, axis=-1)
        h = np.clip(r - R_EARTH, 0.0, None)
        rho_R, rho_M = np.exp(-h / H_RAYLEIGH), np.exp(-h / H_MIE)
        beta = BETA_R[None, None, :] * rho_R[..., None] + beta_m * rho_M[..., None]
        T_view = np.exp(-tau_view)

        # (d) 太阳方向: 本影遮挡判定 + 到大气顶的透射率
        b_s = p @ sun
        shadowed = (b_s < 0) & (r * r - b_s * b_s < R_EARTH ** 2)
        t_disc = b_s * b_s - (r * r - R_ATMO ** 2)
        t_exit = -b_s + np.sqrt(np.clip(t_disc, 0.0, None))
        dt = t_exit / n_sun
        tau_sun = np.zeros((H, W, 3))
        for j in range(n_sun):
            q = p + ((j + 0.5) * dt)[..., None] * sun
            hq = np.clip(np.linalg.norm(q, axis=-1) - R_EARTH, 0.0, None)
            tau_sun += (BETA_R[None, None, :] * np.exp(-hq / H_RAYLEIGH)[..., None]
                        + beta_m * np.exp(-hq / H_MIE)[..., None]) * dt[..., None]
        T_sun = np.exp(-tau_sun)
        T_sun[shadowed] = 0.0                     # 本影内无直射阳光

        # (e) 本点散射系数 × 相函数, 累加到辐射亮度
        scattering = (BETA_R[None, None, :] * rho_R[..., None] * P_R[..., None]
                      + beta_m * rho_M[..., None] * P_M[..., None])
        L += T_view * scattering * T_sun * ds[..., None]
        tau_view = tau_view + beta * ds[..., None]
    return L


# --- 步骤 4: 计算接口: 给定太阳高度下的西方天空 -----------------------------
def compute_sky(sun_alt_deg, sun_az_deg=270.0, turbidity=5.0, alt_max_deg=60.0,
                az_min_deg=180.0, az_max_deg=360.0,
                n_az=361, d_alt=0.5, n_view=48, n_sun=24):
    """
    计算西方天空的单次散射亮度, 返回数据字典 (供 plot_sky 使用)。
      sun_alt_deg : 太阳地平高度 [deg] (负=落下)
      sun_az_deg  : 太阳方位角 [deg] (270=正西)
      turbidity   : 浊度 T (线性映射到气溶胶 Mie 系数)
      alt_max_deg : 地平高度上限 [deg]
      n_az        : 方位方向网格点数
      d_alt       : 高度方向步长 [deg]
    """
    beta_m = BETA_M0 * turbidity / 5.0
    az_grid  = np.linspace(az_min_deg, az_max_deg, n_az)
    alt_grid = np.linspace(0.0, alt_max_deg, int(round(alt_max_deg / d_alt)) + 1)
    AZ, ALT = np.meshgrid(az_grid, alt_grid)
    omega = np.asarray(dir_from_altaz(ALT, AZ))
    sun = dir_from_altaz(sun_alt_deg, sun_az_deg)
    L = single_scattering(omega, sun, beta_m, n_view=n_view, n_sun=n_sun)
    Y = 0.2126 * L[..., 0] + 0.7152 * L[..., 1] + 0.0722 * L[..., 2]   # 视亮度
    return dict(L=L, Y=Y, az_grid=az_grid, alt_grid=alt_grid, AZ=AZ, ALT=ALT,
                sun_alt_deg=float(sun_alt_deg), sun_az_deg=float(sun_az_deg),
                turbidity=float(turbidity), alt_max_deg=float(alt_max_deg))


# --- 步骤 5: 统一绘图函数: 把数据字典画成最终三联图 -------------------------
def plot_sky(data, save_path=None, dpi=150):
    """
    (a) 相对亮度图 (对数)  (b) RGB 物理渲染  (c) 正西方向亮度剖面。
    返回 matplotlib Figure。save_path 非空时顺便保存。
    """
    L, Y = data['L'], data['Y']
    az_grid, alt_grid = data['az_grid'], data['alt_grid']
    AZ, ALT = data['AZ'], data['ALT']
    sun_az, sun_alt, T = data['sun_az_deg'], data['sun_alt_deg'], data['turbidity']
    Ymax = Y.max() if Y.max() > 0 else 1.0

    fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=(16, 5),
                                        gridspec_kw={'width_ratios': [3, 1.6, 1.6]})

    # (a) 相对视亮度图 (对数); 0 -> NaN 画成黑底, 避免对数伪影
    axA.set_facecolor('black')
    if np.any(Y > 0):                          # 有正数据才可用对数色标
        Yplot = np.where(Y > 0, Y, np.nan)
        cmapA = plt.get_cmap('inferno').copy(); cmapA.set_bad('black')
        mesh = axA.pcolormesh(AZ, ALT, Yplot, cmap=cmapA,
                              norm=LogNorm(vmin=Ymax * 1e-6, vmax=Ymax), shading='auto')
        fig.colorbar(mesh, ax=axA, pad=0.01).set_label('相对视亮度')
    else:                                      # 全黑帧 (无被照亮的空气)
        axA.text(0.5, 0.5, '全黑 (无阳光照射)', ha='center', va='center',
                 color='gray', transform=axA.transAxes)
    axA.axvline(sun_az, color='cyan', ls='--', lw=1.2)
    axA.set_xticks([180, 225, 270, 315, 360])
    axA.set_xticklabels(['S 180°', 'SW 225°', 'W 270°', 'NW 315°', 'N 360°'])
    axA.set_xlabel('方位角 Azimuth (deg)'); axA.set_ylabel('地平高度 Altitude (deg)')
    axA.set_title(f'物理单次散射: 相对亮度 (T={T:.0f}, 太阳 {sun_alt:.1f}°)', fontsize=10)

    # (b) RGB 物理渲染 (按最大视亮度归一化 + gamma)
    rgb = np.clip((L / Ymax) ** (1 / 2.2), 0, 1)
    axB.imshow(rgb, aspect='auto', origin='lower',
               extent=[az_grid[0], az_grid[-1], alt_grid[0], alt_grid[-1]])
    axB.axvline(sun_az, color='cyan', ls='--', lw=1.0)
    axB.set_xticks([180, 270, 360]); axB.set_xticklabels(['S', 'W', 'N'])
    axB.set_xlabel('方位角'); axB.set_ylabel('地平高度 (deg)')
    axB.set_title('物理渲染 (RGB, 单次散射)', fontsize=10)

    # (c) 正西方向亮度随高度角的变化
    colw = int(np.argmin(np.abs(az_grid - sun_az)))
    y0 = Y[0, colw] if Y[0, colw] > 0 else 1.0
    axC.plot(Y[:, colw] / y0, alt_grid, color='#e76f51', lw=2, label='物理散射 (单次)')
    axC.set_ylim(0, data['alt_max_deg']); axC.set_xscale('log')
    axC.set_xlabel('相对亮度'); axC.set_ylabel('地平高度 (deg)')
    axC.set_title('正西方向亮度剖面', fontsize=10)
    axC.grid(alpha=0.3, which='both'); axC.legend(fontsize=9)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=dpi)
    return fig


# --- 步骤 6: 演示 -----------------------------------
data = compute_sky(sun_alt_deg=-10.0)
fig = plot_sky(data)
fig.savefig('physical_scattering_western_sky.png', dpi=150)
plt.show()
_colw = int(np.argmin(np.abs(data['az_grid'] - data['sun_az_deg'])))
print(f"[物理] T={data['turbidity']:.0f}, 太阳 {data['sun_alt_deg']:.1f}°, "
      f"西地平相对亮度={data['Y'][0, _colw]:.3e}, 高度{data['alt_max_deg']:.0f}°={data['Y'][-1, _colw]:.3e}")
