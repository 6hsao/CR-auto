import numpy as np
from PIL import Image

def tune_detector():
    try:
        img = Image.open("diagnostic_screenshot.png")
    except Exception:
        print("未找到 diagnostic_screenshot.png")
        return
        
    img_array = np.array(img)
    
    # 检测大厅对战按钮 (黄色)
    # y=900~1020, x=250~470
    button_region = img_array[900:1020, 250:470, :]
    mean_btn = np.mean(button_region, axis=(0, 1))
    print(f"对战按钮区域平均颜色: R={mean_btn[0]:.1f}, G={mean_btn[1]:.1f}, B={mean_btn[2]:.1f}")
    
    # 尝试更精准的找对战按钮
    yellow_target = np.array([255, 200, 50])
    diff = np.abs(button_region.astype(int) - yellow_target)
    mask = np.all(diff < 60, axis=2)
    yellow_pixels = np.sum(mask)
    print(f"黄色像素数量: {yellow_pixels} / {mask.size} ({yellow_pixels/mask.size*100:.1f}%)")
    
    # 检测战斗界面的圣水条 (紫色/粉红色通常是10费，平时是粉色？不，圣水是粉紫色的滴)
    # 让我们检查底部的颜色
    elixir_region = img_array[1150:1250, 100:600, :]
    print(f"底部圣水区域平均颜色: R={np.mean(elixir_region[:,:,0]):.1f}, G={np.mean(elixir_region[:,:,1]):.1f}, B={np.mean(elixir_region[:,:,2]):.1f}")

if __name__ == "__main__":
    tune_detector()