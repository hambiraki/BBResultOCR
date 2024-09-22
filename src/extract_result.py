import sys
from PIL import Image
import pyocr
import easyocr
import pytesseract
import cv2
import numpy as np
from constant import *
from image import ImageRapper

# 勝利文字の場所
WIN_LEFT = 0.53
WIN_RIGHT = 0.81
WIN_TOP = 0.07
WIN_BOTTOM = 0.14

# 名前の場所 単位は割合
BLUE_TEAM_NAME_LEFT = 0.456
BLUE_TEAM_NAME_RIGHT = 0.61
RED_TEAM_NAME_LEFT = 0.755
RED_TEAM_NAME_RIGHT = 0.90
NAME_HEIGHT = 0.028

# 名前の上辺の高さ
NAME_TOP_LIST = [0.135, 0.198, 0.263, 0.327, 0.391, 0.454, 0.518, 0.583, 0.646, 0.711]

# MVPの場所 単位は割合
BLUE_TEAM_MVP_LEFT = 0.44
BLUE_TEAM_MVP_RIGHT = 0.59
RED_TEAM_MVP_LEFT = 0.739
RED_TEAM_MVP_RIGHT = 0.88
MVP_MARGIN_HEIGHT = 0.002
MVP_HEIGHT = 0.028


# 黒の閾値
BLACK_THRESHOLD = 32


def main():
    """
    どーすんだこれ
    """
    # リザルト画面の画像読み込み
    ## リザルト画面画像のパスの読み込み
    if len(sys.argv) != 2:
        print("Usage: python extract_result.py <path_to_image>")
        return
    ## 画像の読み込み
    path_to_image = sys.argv[1]
    color_image = ImageRapper(path_to_image)

    # 前処理
    ## トリミング
    ## 角度調整
    ## モノクロ化(OCRで認識しやすいように)
    binary_image = color_image.copy().toBinary()
    # データの抽出
    width, height = color_image.asPil().size
    print(width, height)

    ## 勝敗判定
    ### 勝利文字がどちらにあるか
    win_image = color_image.copy().trim(
        slice(int(height * WIN_TOP), int(height * WIN_BOTTOM)),
        slice(int(width * WIN_LEFT), int(width * WIN_RIGHT)),
    )
    win_image.save("C:/Users/hambi/work/BBResultOCR/image/win.jpg")

    is_blue_alpha_win = contains_icon(win_image, ImageRapper(BLUE_ALPHA_WIN))
    is_blue_beta_win = contains_icon(win_image, ImageRapper(BLUE_BETA_WIN))
    is_blue_win = is_blue_alpha_win or is_blue_beta_win
    is_red_alpha_win = contains_icon(win_image, ImageRapper(RED_ALPHA_WIN))
    is_red_beta_win = contains_icon(win_image, ImageRapper(RED_BETA_WIN))
    is_red_win = is_red_alpha_win or is_red_beta_win

    if is_blue_win == is_red_win:
        raise Exception("どちらが勝利したか読み取れませんでした。")

    ### 割り勝ち判定
    is_breaked = False
    ### 圧勝/大敗判定
    is_completely = False
    ### 早割り判定
    is_early = False

    blue_result = WIN_LOSE_RESULT[(is_blue_win, is_breaked, is_completely, is_early)]
    red_result = WIN_LOSE_RESULT[(is_red_win, is_breaked, is_completely, is_early)]

    blue_team = []
    red_team = []
    rank = 0
    for name_top in NAME_TOP_LIST:
        ## 青
        ### 名前の抽出
        rank = rank + 1
        cropped_name_image = binary_image.copy().trim(
            slice(int(width * BLUE_TEAM_NAME_LEFT), int(width * BLUE_TEAM_NAME_RIGHT)),
            slice(int(height * name_top), int(height * (name_top + NAME_HEIGHT))),
        )
        name = extract_text(cropped_name_image)
        cropped_name_image.save(f"C:/Users/hambi/work/BBResultOCR/image/blue{rank}.jpg")
        ### MVP判定
        mvp_result = ""
        cropped_mvp_image = color_image.copy().trim(
            slice(
                int(height * (name_top + NAME_HEIGHT + MVP_MARGIN_HEIGHT)),
                int(height * (name_top + NAME_HEIGHT + MVP_MARGIN_HEIGHT + MVP_HEIGHT)),
            ),
            slice(
                int(width * BLUE_TEAM_MVP_LEFT),
                int(width * BLUE_TEAM_MVP_RIGHT),
            ),
        )
        cropped_mvp_image.save(
            f"C:/Users/hambi/work/BBResultOCR/image/blue_mvp{rank}.jpg"
        )
        for mvp_type, mvp_icon_path in MVP_ICON_FILENAME.items():
            if contains_icon(cropped_mvp_image, mvp_icon_path, 0.9):
                mvp_result += mvp_type
        if mvp_result != "":
            mvp_result = "(" + mvp_result + ")"

        blue_team.append([name, blue_result + mvp_result])

        ## 赤
        ### 名前の抽出
        cropped_name_image = binary_image.crop(
            (
                width * RED_TEAM_NAME_LEFT,
                height * name_top,
                width * RED_TEAM_NAME_RIGHT,
                height * (name_top + NAME_HEIGHT),
            )
        )
        name = extract_text(cropped_name_image)
        cropped_name_image.save(f"C:/Users/hambi/work/BBResultOCR/image/red{rank}.jpg")
        ### MVP判定
        mvp_result = ""
        cropped_mvp_image = cv2.imread(path_to_image)[
            int(height * (name_top + NAME_HEIGHT + MVP_MARGIN_HEIGHT)) : int(
                height * (name_top + NAME_HEIGHT + MVP_MARGIN_HEIGHT + MVP_HEIGHT)
            ),
            int(width * RED_TEAM_MVP_LEFT) : int(width * RED_TEAM_MVP_RIGHT),
        ]
        cv2.imwrite(
            f"C:/Users/hambi/work/BBResultOCR/image/red_mvp{rank}.jpg",
            cropped_mvp_image,
        )
        for mvp_type, mvp_icon_path in MVP_ICON_FILENAME.items():
            if contains_icon(cropped_mvp_image, mvp_icon_path, 0.9):
                mvp_result += mvp_type
        if mvp_result != "":
            mvp_result = "(" + mvp_result + ")"

        red_team.append([name, red_result + mvp_result])

    print(blue_team)
    print(red_team)

    # csvファイルへの書き出し


def extract_text(image: ImageRapper):
    """
    文字列の抽出
    """
    # easyocr
    reader = easyocr.Reader(["en", "ja"])
    numpy_image = np.array(image)
    results = reader.readtext(numpy_image)
    easyocr_text = " ".join([result[1] for result in results])
    easyocr_confidence = min([result[2] for result in results])

    pytesseract_results = pytesseract.image_to_data(
        image.asPil(),
        lang="jpn",
        config=r"--psm 6",
        output_type=pytesseract.Output.DICT,
    )
    pytesseract_text = "".join(
        [
            text
            for text, conf in zip(
                pytesseract_results["text"], pytesseract_results["conf"]
            )
            if conf > 10
        ]
    )
    pytesseract_confs = [conf for conf in pytesseract_results["conf"] if conf > 30]
    pytesseract_conf = 30 if pytesseract_confs is None else min(pytesseract_confs)

    if easyocr_confidence > pytesseract_conf:
        return easyocr_text
    else:
        return pytesseract_text


def contains_icon(image: ImageRapper, template: ImageRapper, threshold=0.8):
    """
    image_pathの画像にtemplateの画像が存在するか判定する
    """
    result = cv2.matchTemplate(
        image.asMatLike(), template.asMatLike(), cv2.TM_CCOEFF_NORMED
    )

    locations = np.where(result >= threshold)

    return len(locations[0]) > 0


if __name__ == "__main__":
    main()
