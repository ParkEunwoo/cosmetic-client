import cv2
import numpy as np
from skimage.filters import gaussian

# only for hair
def sharpen(img):
    img = img * 1.0
    gauss_out = gaussian(img, sigma=5, multichannel=True)

    alpha = 1.5
    img_out = (img - gauss_out) * alpha + img

    img_out = img_out / 255.0

    mask_1 = img_out < 0
    mask_2 = img_out > 1

    img_out = img_out * (1 - mask_1)
    img_out = img_out * (1 - mask_2) + mask_2
    img_out = np.clip(img_out, 0, 1)
    img_out = img_out * 255
    return np.array(img_out, dtype=np.uint8)


def hair(image, parsing, part=17, color=[230, 50, 20]):
    b, g, r = color      # ex) [230, 50, 20] == [b, g, r]
    tar_color = np.zeros_like(image) # np.zeros_like() : 다른 배열과 같은 크기의, 0으로 채워진 배열 생성 / y,x,채널 : 3차원 행렬 image
    tar_color[:, :, 0] = b # ex) b=230
    tar_color[:, :, 1] = g
    tar_color[:, :, 2] = r

    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    tar_hsv = cv2.cvtColor(tar_color, cv2.COLOR_BGR2HSV)
    
    # upper_lip or lower_lip
    if part == 12 or part == 13:
        image_hsv[:, :, 0:2] = tar_hsv[:, :, 0:2] # h,s만 바꿔주기(H:색조, S:채도)
    else:
        image_hsv[:, :, 0:1] = tar_hsv[:, :, 0:1] # h만 바꿔주기

    changed = cv2.cvtColor(image_hsv, cv2.COLOR_HSV2BGR) # 다시 BGR로 변환 / 3차원 changed

    # hair
    if part == 17:
        changed = sharpen(changed)
    
    # ***boolean 조건문으로 배열 indexing*** : parsing결과 imaage(배열) 요소값이, hair면 17과 0으로 이루어짐. part(=17)과 다른 parsing부분(=17이 아닌 값)만 인덱싱해서 image(원본)의 인덱싱 결과값으로 대체!
    changed[parsing != part] = image[parsing != part]
    return changed

def makeup(face, parsing):
    image = cv2.imread(face) #ori
    parsing = cv2.imread(parsing) #seg

    table = {
        'hair': 17,
        'upper_lip': 12,
        'lower_lip': 13
    }
    parts = [table['hair'], table['upper_lip'], table['lower_lip']] #[17, 12, 13]
    colors = [[17, 17, 63], [42.75, 63.84, 208.98], [42.75, 63.84, 208.98]] #[b,g,r] 순서

    # 두 변수 part라는 index는 parts를, color는 colors를 동시에 for문을 돌음
    for part, color in zip(parts, colors):
        makeup = hair(image, parsing, part, color) #hair함수에 들어가는 인자 image는 원래 원본이미지 / 한 부분, 한 색상(bgr)씩 들어감 => 3번 돌면 image 완성

    '''
    cv2.imshow('makeup', cv2.resize(makeup, (512, 512)))  # makeup이미지

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    '''

    return makeup