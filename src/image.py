from __future__ import annotations
from PIL import Image
import cv2
import numpy as np
import copy


class ImageRapper:
    """ImageはPILやCV2で直接編集しない"""

    def __init__(self, image_path: str) -> None:
        """"""
        self.image_cv = cv2.imread(image_path)

    # このクラス以外でPILやCV2を直接編集してはならない
    # def fromPil(self, image_pil: Image) -> ImageRapper:
    #     """PIL型 -> OpenCV型"""
    #     new_image = np.array(image_pil, dtype=np.uint8)
    #     if new_image.ndim == 2:  # モノクロ
    #         pass
    #     elif new_image.shape[2] == 3:  # カラー
    #         new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
    #     elif new_image.shape[2] == 4:  # 透過
    #         new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    #     return new_image

    # def fromMatLike(self, image_cv: cv2.typing.MatLike) -> ImageRapper:
    #     """"""
    #     self.image_cv = image_cv

    def asPil(self) -> Image:
        """PIL型"""
        new_image = self.image_cv.copy()
        if new_image.ndim == 2:  # モノクロ
            pass
        elif new_image.shape[2] == 3:  # カラー
            new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
        elif new_image.shape[2] == 4:  # 透過
            new_image = cv2.cvtColor(new_image, cv2.COLOR_BGRA2RGBA)
        new_image = Image.fromarray(new_image)
        return new_image

    def asMatLike(self) -> cv2.typing.MatLike:
        """OpenCV型"""
        return self.image_cv

    def toBinary(self, threshold=30) -> ImageRapper:
        """
        モノクロ化(OCRで認識しやすいように)
        参照透過ではないため元データが変更される
        """
        ### ピクセルごとに処理 黒に近い値を白 (255) に、それ以外を黒 (0) にする
        _, binary_image = cv2.threshold(
            self.image_cv, threshold, 255, cv2.THRESH_BINARY
        )
        self.image_cv = binary_image
        return self

    def trim(self, x_slice: slice, y_slice: slice) -> ImageRapper:
        """
        参照透過ではないため元データが変更される
        """
        self.image_cv = self.image_cv[x_slice, y_slice]
        return self

    def copy(self) -> ImageRapper:
        """"""
        return copy.deepcopy(self)

    def save(self, image_path: str) -> None:
        """"""
        cv2.imwrite(image_path, self.image_cv)
