import sys
from PIL import Image
import pyocr.builders
import pyocr
import cv2
import numpy as np
from constant import *

# 単位は割合
BLUE_TEAM_LEFT = 0.456
BLUE_TEAM_RIGHT = 0.61
RED_TEAM_LEFT = 0.755
RED_TEAM_RIGHT = 0.90
NAME_HEIGHT = 0.028

# 名前の上辺の高さ
NAME_TOP_LIST = [0.135, 0.198, 0.263, 0.327, 0.391, 0.454, 0.518, 0.583, 0.646, 0.711]

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
    color_image = Image.open(path_to_image)

    # 前処理
    ## トリミング
    ## 角度調整
    ## モノクロ化(OCRで認識しやすいように)
    ### グレースケールに変換
    gray_image = color_image.convert("L")
    ### ピクセルごとに処理 黒に近い値を白 (255) に、それ以外を黒 (0) にする
    image = gray_image.point(lambda p: 255 if p < BLACK_THRESHOLD else 0)

    # データの抽出
    width, height = image.size

    ## 勝敗判定
    ### 勝利文字がどちらにあるか
    # 勝利文字の場所
    WIN_LEFT = 0.53
    WIN_RIGHT = 0.81
    WIN_TOP = 0.07
    WIN_BOTTOM = 0.14
    win_image = cv2.imread(path_to_image)[
        int(height * WIN_TOP) : int(height * WIN_BOTTOM),
        int(width * WIN_LEFT) : int(width * WIN_RIGHT),
    ]

    is_blue_win = contains_icon(win_image, BLUE_ALPHA_WIN) or contains_icon(
        win_image, BLUE_BETA_WIN
    )
    is_red_win = contains_icon(win_image, RED_ALPHA_WIN) or contains_icon(
        win_image, RED_BETA_WIN
    )
    if is_blue_win == is_red_win:
        print("どちらが勝利したか読み取れませんでした。")
        raise Exception()

    ### 割り勝ち判定
    is_breaked_base = False
    ### 早割り判定
    is_early = False
    ### 圧勝/大敗判定
    is_completely = False

    if not is_breaked_base and (is_early or is_completely):
        print("コアが割れていないのに早割、圧勝扱いです。")
        raise Exception()
    blue_result, red_result = (
        (
            (WinLoseType.C_WIN, WinLoseType.C_LOSE)
            if is_blue_win and is_completely and not is_early
            else (
                (WinLoseType.WIN, WinLoseType.LOSE)
                if not is_breaked_base and is_blue_win
                else (
                    (WinLoseType.LOSE, WinLoseType.WIN)
                    if not is_breaked_base and is_red_win
                    else None
                )
            )
        ),
        None,
    )
    if not is_breaked_base:
        if is_blue_win:
            blue_result = WinLoseType.WIN
            red_result = WinLoseType.LOSE

    ## 名前の抽出
    blue_team = []
    red_team = []
    rank = 0
    for name_top in NAME_TOP_LIST:
        rank = rank + 1
        cropped_image = image.crop(
            (
                width * BLUE_TEAM_LEFT,
                height * name_top,
                width * BLUE_TEAM_RIGHT,
                height * (name_top + NAME_HEIGHT),
            )
        )
        name = extract_text(cropped_image)
        blue_team.append(name)
        cropped_image.save(f"C:/Users/hambi/work/BBResultOCR/image/blue{rank}.jpg")

        cropped_image = image.crop(
            (
                width * RED_TEAM_LEFT,
                height * name_top,
                width * RED_TEAM_RIGHT,
                height * (name_top + NAME_HEIGHT),
            )
        )
        name = extract_text(cropped_image)
        red_team.append(name)
        cropped_image.save(f"C:/Users/hambi/work/BBResultOCR/image/red{rank}.jpg")

    print(blue_team)
    print(red_team)
    ## MVP判定

    # csvファイルへの書き出し


def extract_text(cropped_image):
    """
    文字列の抽出
    """
    tools = pyocr.get_available_tools()
    assert len(tools) != 0
    tool = tools[0]  # pytesseract
    return tool.image_to_string(
        cropped_image,
        lang="jpn",
        builder=pyocr.builders.TextBuilder(
            tesseract_layout=6  # Assume a single uniform block of text.
        ),
    )


def contains_icon(image: cv2.typing.MatLike, template_path: str, threshold=0.8):
    """
    image_pathの画像にtemplateの画像が存在するか判定する
    """
    # 画像の読み込み
    template = cv2.imread(template_path)

    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

    locations = np.where(result >= threshold)

    return len(locations[0]) > 0


if __name__ == "__main__":
    main()
