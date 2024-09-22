"""
定数
"""

import enum

# win, break, completely, early
WIN_LOSE_RESULT = {
    (True, True, True, False): "〇圧勝",
    (True, True, False, False): "〇割勝",
    (True, False, False, False): "〇勝利",
    (True, True, True, True): "〇早圧",
    (True, True, False, True): "〇早勝",
    (False, True, False, True): "×早敗",
    (False, True, True, True): "×早大",
    (False, False, False, False): "×敗北",
    (False, True, False, False): "×割敗",
    (False, True, True, False): "×大敗",
}


# class WinLoseType(enum.Enum):
#     """勝敗 種類"""

#     # COMPLETELY, BREAK, EARLY
#     C_WIN = "〇圧勝"
#     B_WIN = "〇割勝"
#     WIN = "〇勝利"
#     EC_WIN = "〇早圧"
#     E_WIN = "〇早勝"
#     E_LOSE = "×早敗"
#     EC_LOSE = "×早大"
#     LOSE = "×敗北"
#     B_LOSE = "×割敗"
#     C_LOSE = "×大敗"


# MVP名とアイコン画像のファイル名
MVP_PATH = "image/mvp/"
MVP_ICON_FILENAME = {
    "撃破金": MVP_PATH + "MVP_BREAK_GOLD.jpg",
    "コア金": MVP_PATH + "MVP_CORE_GOLD.jpg",
    "防衛金": MVP_PATH + "MVP_DEFENSE_GOLD.jpg",
    "進行金": MVP_PATH + "MVP_PROGRESS_GOLD.jpg",
    # "偵察金": MVP_PATH + "MVP_SCOUT_GOLD.jpg",
    # "撃破緑": MVP_PATH + "MVP_BREAK_GREEN.jpg",
    "コア緑": MVP_PATH + "MVP_CORE_GREEN.jpg",
    "防衛緑": MVP_PATH + "MVP_DEFENSE_GREEN.jpg",
    # "進行緑": MVP_PATH + "MVP_PROGRESS_GREEN.jpg",
    "偵察緑": MVP_PATH + "MVP_SCOUT_GREEN.jpg",
}

# 勝利画像パス
WIN_PATH = "image/win/"
BLUE_ALPHA_WIN = WIN_PATH + "win_alpha_beta.jpg"
BLUE_BETA_WIN = WIN_PATH + "win_beta_alpha.jpg"
RED_BETA_WIN = WIN_PATH + "alpha_beta_win.jpg"
RED_ALPHA_WIN = WIN_PATH + "beta_alpha_win.jpg"
