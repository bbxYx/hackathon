from flask import render_template, Blueprint, request, jsonify
import cv2
from imutils.perspective import four_point_transform
import pytesseract
import cv2
from googletrans import Translator


class OCRProcessor:
    def __init__(self, file_path):
        self.file_path = file_path

    # 이미지를 ocr로 바꾸는 함수
    def run_tesseract_ocr(self):
        # # 이미지 불러오기
        # image = cv2.imread(self.file_path) 

        # 변경할 이미지를 담을 빈 리스트
        image_list_title = []
        image_list = []

        # 원본 img(org_image) 보관용 변수선언
        org_image = image.copy()

        # image사이즈조절
        image = cv2.resize(image, dsize=(200, image.shape[0]))
        # 원본이미지/크기조절이미지의 비율을 변수ratio로 선언 >> 추후 다시 원래대로 돌릴때 사용
        ratio = org_image.shape[1] / float(image.shape[1])

        # 이미지를 grayscale로 변환하고 blur를 적용
        # 모서리를 찾기위한 이미지 연산
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 20, 100)

        # 변환한 이미지들을 list에 저장
        image_list_title = ['gray', 'blurred', 'edged']
        image_list = [gray, blurred, edged]

        # contours(같은 값을 가진 곳을 연결한 선. 이미지의 외곽선을 검출하기 위해 사용) 를 찾아 크기순으로 정렬
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(contours, key=cv2.contourArea, reverse=True)

        receiptCnt = None

        # 정렬된 contours를 반복문으로 수행하며 4개의 꼭지점을 갖는 도형을 검출
        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            # contours가 크기순으로 정렬되어 있기때문에 제일 첫번째 사각형을 영수증 영역으로 판단하고 break
            if len(approx) == 4:
                receiptCnt = approx
                break
    
    # 만약 추출한 윤곽이 없을 경우 오류처리
        if receiptCnt is None:
            raise Exception(("인식에 실패하였습니다. 다른 이미지를 넣어주세요."))
    
        output = image.copy()
        cv2.drawContours(output, [receiptCnt], -1, (0, 255, 0), 2)

        image_list_title.append("Receipt Outline")
        image_list.append(output)

        # 원본 이미지에 찾은 윤곽을 기준으로 이미지를 비율맞추고 보정
        receipt = four_point_transform(org_image, receiptCnt.reshape(4, 2) * ratio)
    
        # ocr적용
        options = "--psm 4"

        text = pytesseract.image_to_string(cv2.cvtColor(receipt, cv2.COLOR_BGR2RGB), lang='kor+eng', config=options)

        # 문자가 인식되지 않았을 경우(전처리를 하지않고 전처리를 하지않은 이미지에서 문자를 찾아보도록함 - 윤곽을 잘못따는 경우 대비)
        if len(text)==0:
            result = pytesseract.image_to_string(cv2.cvtColor(org_image, cv2.COLOR_BGR2RGB), lang='kor+eng', config=options)

        else : result=text

        if len(result) != 0:
            return result
        
        else:
            return '문자가 인식되지 않았습니다. 다시 출력해주세요.'

    # ocr로 만든 문자를 번역하여 보여주기
    def trans_ocr(self, dest='en'):
        ocr_result = self.run_tesseract_ocr()
        lines = ocr_result.split('\n')
        translator = Translator()

        translations = []

        for line in lines:
            translation = translator.translate(line, dest=dest).text
            translations.append(translation)
        result = '\n'.join(translations)
    
        return result
    
trans_ocr = Blueprint('trans_ocr', __name__, url_prefix='/ocr')

@trans_ocr.route('/', methods=['GET'])
def ocr_home():
    return render_template('ocr.html')

# @trans_ocr.route('/trans', methods=['POST'])
# def trans_img():
#     if 'file' not in request.files:
#         return {'error': 'No file part'}

#     file = request.files['file']

#     if file.filename == '':
#         return {'error': 'No selected file'}
#     try:
#         img_bytes = file.read()
#         ocr_processor = OCRProcessor(img_bytes)
#         ocr_result = ocr_processor.run_tesseract_ocr()
#         return {'result': ocr_result}
    
#     except Exception as e:
#         return {'error': str(e)}
    

@trans_ocr.route('/trans', methods=['POST'])
def trans_img():

    file = request.files.get('file')
    
    img_ = file.read()

    if __name__ == "__main__":
        # OCRProcessor 클래스의 인스턴스 생성 및 이미지 지정
        ocr_processor = OCRProcessor(img_)

        # 한글 텍스트 추출 
        ocr_result = ocr_processor.run_tesseract_ocr()

        # # 추출된 텍스트 번역
        # translated_text = ocr_processor.trans_ocr(dest='en')

        # return translated_text
        
    return ocr_result
