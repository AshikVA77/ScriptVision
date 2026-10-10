import cv2
import numpy as np
import tempfile


def preprocess_image(image_path):

    # -----------------------------
    # Read image
    # -----------------------------
    image = cv2.imread(image_path)

    if image is None:
        raise Exception("Image not found")

    # -----------------------------
    # Resize
    # -----------------------------
    h, w = image.shape[:2]

    if w < 1500:
        scale = 1500 / w

        image = cv2.resize(
            image,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC
        )

    # -----------------------------
    # Convert BGR to HSV
    # -----------------------------
    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    # -----------------------------
    # Detect blue handwriting
    # -----------------------------
    lower_blue = np.array([100, 60, 40])
    upper_blue = np.array([130, 255, 255])

    blue_mask = cv2.inRange(
        hsv,
        lower_blue,
        upper_blue
    )

    # -----------------------------
    # Remove small noise
    # -----------------------------
    kernel = np.ones(
        (2, 2),
        np.uint8
    )

    blue_mask = cv2.morphologyEx(
        blue_mask,
        cv2.MORPH_OPEN,
        kernel
    )

    # -----------------------------
    # Convert to black text
    # on white background
    # -----------------------------
    processed = 255 - blue_mask

    # -----------------------------
    # Convert to 3-channel BGR
    # -----------------------------
    processed = cv2.cvtColor(
        processed,
        cv2.COLOR_GRAY2BGR
    )

    # -----------------------------
    # Save temporary image
    # -----------------------------
    temp = tempfile.NamedTemporaryFile(
        suffix=".png",
        delete=False
    )

    cv2.imwrite(
        temp.name,
        processed
    )

    return temp.name