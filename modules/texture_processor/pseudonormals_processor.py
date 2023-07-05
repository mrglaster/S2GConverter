import PIL.Image
import cv2
import colortrans
import os
import numpy as np
from PIL import Image
from PIL import ImageStat
from PIL import ImageEnhance


def delta_brightness(source_texture: str, overlay_texture: str) -> float:
    """Calculates brightness value difference between two textures"""
    return ImageStat.Stat(Image.open(overlay_texture).convert('L')).mean[0] - ImageStat.Stat(Image.open(source_texture).convert('L')).mean[0]


def adjust_saturation(img: PIL.Image.Image, saturation_factor: float) -> PIL.Image.Image:
    """Modifies saturation of the image"""
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(saturation_factor)
    return img


def change_brightness(image_path: str, value: int = 30) -> PIL.Image.Image:
    """Changes brightness of the image"""
    img = cv2.imread(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = cv2.add(v, value)
    v[v > 255] = 255
    v[v < 0] = 0
    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img


def clear_pnm_processing_trash() -> None:
    """Clears temp textures generated during the pseudo normal maps processing"""
    os.remove('combined.png')
    os.remove('combined_result.png')
    for i in os.listdir():
        if 'grayscale' in i:
            os.remove(i)


def generate_pseudo_normal_map(source_texture: str, normal_map: str) -> None:
    """Generates pseudo normal map and replaces the original texture with itself"""
    img = Image.open(normal_map).convert('L')
    grayscale_name = normal_map[:len(normal_map)-4]+"_grayscale.png"
    try:
        img.save(grayscale_name)
    except:
        pass
    background = cv2.imread(source_texture)
    overlay = cv2.imread(grayscale_name)
    added_image = cv2.addWeighted(background, 0.92, overlay, 1, 0)
    cv2.imwrite('combined.png', added_image)
    value = delta_brightness(source_texture, 'combined.png')
    result = change_brightness('combined.png', -1*value)
    cv2.imwrite('combined_result.png', result)
    img_pil = adjust_saturation(Image.open('combined_result.png'), 3)
    clear_pnm_processing_trash()
    reference = np.array(Image.open(source_texture).convert('RGB'))
    content = np.array(img_pil.convert('RGB'))
    result = Image.fromarray(colortrans.transfer_reinhard(content, reference))
    result.save(source_texture)

