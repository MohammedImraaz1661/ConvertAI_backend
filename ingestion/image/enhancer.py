import cv2
import numpy as np
import os
from typing import List, Tuple


class ImageEnhancer:
    def __init__(
        self,
        debug: bool = False,
        debug_dir: str = "debug_images"
    ):
        """
        debug      : Save original + enhanced images
        debug_dir  : Directory to store debug images
        """
        self.debug = debug
        self.debug_dir = debug_dir

        if self.debug:
            os.makedirs(self.debug_dir, exist_ok=True)

    # -------------------------------------------------
    # IMAGE LOADING (UPLOAD / TEMP FILE SUPPORT)
    # -------------------------------------------------
    def load_image(self, image_path: str):
        """
        Load image from disk.
        Raises error if image is invalid.
        """
        image = cv2.imread(image_path)

        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")

        if self.debug:
            cv2.imwrite(
                os.path.join(self.debug_dir, "00_original_uploaded.png"),
                image
            )

        return image

    # -------------------------------------------------
    # ENHANCEMENT PIPELINE
    # -------------------------------------------------
    def enhance_variants(self, img) -> List[Tuple[str, np.ndarray]]:
        """
        Generates progressive enhancement variants.
        Returns list of (variant_name, image)
        """
        variants = []

        # ---------- Level 0: Original ----------
        variants.append(("original", img))

        # ---------- Level 1: Grayscale ----------
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        variants.append(("gray", gray))

        # ---------- Level 2: Denoise ----------
        denoised = cv2.fastNlMeansDenoising(
            gray,
            h=30,
            templateWindowSize=7,
            searchWindowSize=21
        )
        variants.append(("denoise", denoised))

        # ---------- Level 3: CLAHE (BEST FOR OCR) ----------
        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        ).apply(denoised)
        variants.append(("clahe", clahe))

        # ---------- Level 4: Mild Sharpen ----------
        sharpen_kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])
        sharpen = cv2.filter2D(clahe, -1, sharpen_kernel)
        variants.append(("sharpen", sharpen))

        # ---------- Level 5: Adaptive Threshold (LAST RESORT) ----------
        threshold = cv2.adaptiveThreshold(
            clahe,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        variants.append(("threshold", threshold))

        # ---------- SAVE DEBUG IMAGES ----------
        if self.debug:
            for idx, (name, image) in enumerate(variants):
                filename = f"{idx:02d}_{name}.png"
                path = os.path.join(self.debug_dir, filename)
                cv2.imwrite(path, image)

        return variants

    # -------------------------------------------------
    # FULL FLOW (LOAD → ENHANCE)
    # -------------------------------------------------
    def process_image(self, image_path: str):
        """
        Convenience method:
        Loads image and returns enhancement variants.
        """
        image = self.load_image(image_path)
        return self.enhance_variants(image)
