from flask import render_template, Blueprint
from skimage.metrics import structural_similarity as ssim
from skimage import color
import cv2
from flask import request
import numpy as np
import base64

hangle_bs = Blueprint('hangle_bs', __name__, url_prefix='/hangle')

def print_ssim(img1, img2):

    # 영상을 그레이스케일로 변환 (SSIM 함수는 그레이스케일 이미지를 사용함)
    gray_image1 = color.rgb2gray(img1)
    gray_image2 = color.rgb2gray(img2)

    # SSIM 계산
    ssim_value, _ = ssim(gray_image1, gray_image2, data_range=255, full=True)

    # 결과 출력
    if ssim_value >= 0.95 :
        return ('wow! excelent!')
    elif ssim_value >= 0.92 and ssim_value<0.95: return ('great!')
    elif ssim_value >=0.89 and ssim_value<0.92 : return ('good~')
    else : return ('try again')

def base64_to_cv2(base64_image):
    # "data:image/png;base64," 부분을 제거하고 base64 데이터를 디코딩합니다.
    image_data = base64.b64decode(base64_image.split(',')[1])
    # 바이너리 데이터를 넘파이 배열로 읽어들입니다.
    image_array = np.frombuffer(image_data, np.uint8)
    # 넘파이 배열을 이미지로 변환합니다.
    image_cv2 = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image_cv2

@hangle_bs.route('/', methods=['GET', 'POST'])
def return_home():
    return render_template('hangle.html')

@hangle_bs.route('/check_ssim', methods=['POST'])
def save_img():
    drawed_image = request.form.get("now_drawed_image")
    draw_np = base64_to_cv2(drawed_image)
    draw = cv2.cvtColor(draw_np, cv2.COLOR_RGB2BGR)
    draw=cv2.resize(draw,(420,50))

    now_text_image = request.form.get("now_text_image")
    now_image_url=now_text_image.split('00/')[-1]
    now_image = cv2.imread(now_image_url)
    now_image=cv2.resize(now_image,(420,50))

    return print_ssim(now_image, draw)
