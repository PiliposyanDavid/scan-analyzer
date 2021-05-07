import os
import json
from PIL import ImageFont, ImageDraw, Image
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import requests


def trim_img(img):
    img = img.convert('L')
    if np.array(img)[0, 0] == 255:
        img = Image.fromarray(np.subtract(255, img))
    return img.crop(img.getbbox())


def draw_font_sample(font_file, text, trim=True, font_size=16):
    img = Image.new('RGB', (300, 150), "black")
    font = ImageFont.truetype(font_file, font_size)
    draw = ImageDraw.Draw(img)
    draw.text((30, 30), text, font=font)

    return trim_img(img) if trim else img


def cmp_images(img1, img2):
    img2 = img2.resize(img1.size)
    for i in range(1, 7):
        s = np.divide(img1.size, i).astype(np.int32)
        tmg1 = np.array(img1.resize(s), dtype=np.float32) / 255
        tmg2 = np.array(img2.resize(s), dtype=np.float32) / 255
        tmp1 = (tmg1 > 0.001) * 1.0
        tmp2 = (tmg1 > 0.001) * 1.0
        diff = np.abs(tmg1 - tmg2)

        err = np.count_nonzero(diff > 0.01) / (np.count_nonzero(tmp1) + np.count_nonzero(tmg2)) * i
        yield err + 1


def find_match_with_image(img, font_file_map, text, use_scale=True, font_size=16, best_matches=5):
    all_fonts = []
    for k, v in tqdm(font_file_map.items()):
        fi = draw_font_sample(v, text, font_size=font_size)
        size_diff = np.product(np.divide(img.size, fi.size))
        size_diff = max(size_diff, 1 / size_diff)
        f_vec = [*cmp_images(fi, img)]
        if use_scale:
            f_vec.insert(0, size_diff)

        ratio_of_ratios = np.divide(*img.size) / np.divide(*fi.size)

        ratio_of_ratios = max(ratio_of_ratios, 1 / ratio_of_ratios)

        f_vec.insert(0, ratio_of_ratios * 3)
        total_error = np.prod(f_vec)
        all_fonts.append((k, fi, f_vec, total_error))
    ff = sorted(all_fonts, key=lambda e: e[3], reverse=False)[:best_matches]
    for i, (name, fi, d, p) in enumerate(ff):
        plt.figure(figsize=(15, 3), dpi=72)
        plt.subplot(1, 2, 1)
        plt.imshow(img, cmap='gray')
        plt.subplot(1, 2, 2)
        plt.imshow(fi, cmap='gray')
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        yield name, base64.b64encode(buf.read()).decode('ascii')


def find_font(image_file_or_font, font_file_map, text, font_size, best_matches):
    if os.path.splitext(image_file_or_font)[-1] in ['.png', '.jpg', '.JPEG', '.JPG', '.webp']:
        return find_match_with_image(trim_img(Image.open(image_file_or_font)), font_file_map, text=text,
                                     use_scale=False, font_size=font_size, best_matches=best_matches)
    else:
        return find_match_with_image(draw_font_sample(image_file_or_font, text=text), font_file_map, text=text,
                                     font_size=font_size, best_matches=best_matches)


def load_listing(pa_fonts_json, pa_fonts_dir):
    with open(pa_fonts_json) as f:
        pa_fonts = json.load(f)['response']
    return dict([(i['name'], os.path.join(pa_fonts_dir, os.path.basename(i['url']))) for i in pa_fonts])


def load_fonts():
    print("Start downloading !!")
    pa_fonts_json = 'pa_fonts.json'
    pa_fonts_dir = 'pa_fonts'

    if not os.path.exists(pa_fonts_dir):
        os.mkdir(pa_fonts_dir)

    response = requests.get(
        'https://api.picsart.com/stage-versions/tmp-branch-test/api/shop/fonts/items')
    with open(pa_fonts_json, 'wb') as fd:
        for chunk in response.iter_content(100):
            fd.write(chunk)

    with open(pa_fonts_json) as f:
        pa_fonts = json.load(f)['response']

    urls = []

    for i in pa_fonts:
        urls.append(f"{i['url']}")

    for url in urls:
        r = requests.get(url)
        with open(pa_fonts_dir + '/' + get_file_name_from_url(url), 'wb') as f:
            f.write(r.content)
    print("Finish downloading !!")


def get_file_name_from_url(url):
    return url[slice(url.rindex('/') + 1, len(url))]


def main(image_file_or_font, pa_fonts_json='pa_fonts.json', pa_fonts_dir='pa_fonts', text='ABCQabilqpvw', font_size=16,
         best_matches=5, output='public/result.html'):
    font_file_map = load_listing(pa_fonts_json, pa_fonts_dir)
    result = ''
    for i, (name, img) in enumerate(
            find_font(image_file_or_font, font_file_map, text, font_size, best_matches)):
        result += f"""
                        <div>
                          <p>{i + 1}) {name}</p>
                          <img src="data:image/png;base64,{img}" alt="Data of {name}" />
                        </div>
                        
                        """
    return result
