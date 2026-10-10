import os
import fitz


SUPPORTED_IMAGE_TYPES = [
    ".jpg",
    ".jpeg",
    ".png"
]

SUPPORTED_FILE_TYPES = [
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png"
]


def prepare_answer_script(file_path):

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            "Answer script file not found."
        )

    extension = os.path.splitext(
        file_path
    )[1].lower()


    # ---------------------------------------------
    # Check supported file type
    # ---------------------------------------------

    if extension not in SUPPORTED_FILE_TYPES:
        raise ValueError(
            "Unsupported file type. "
            "Use PDF, JPG, JPEG or PNG."
        )


    # ---------------------------------------------
    # Image file
    # ---------------------------------------------

    if extension in SUPPORTED_IMAGE_TYPES:

        return {
            "file_type": "image",
            "pages": [file_path],
            "total_pages": 1
        }


    # ---------------------------------------------
    # PDF file
    # ---------------------------------------------

    if extension == ".pdf":

        output_directory = os.path.join(
            os.path.dirname(file_path),
            "processed_pages"
        )

        os.makedirs(
            output_directory,
            exist_ok=True
        )


        pdf = fitz.open(file_path)

        pages = []


        for page_number, page in enumerate(pdf):

            output_path = os.path.join(
                output_directory,
                f"{os.path.splitext(os.path.basename(file_path))[0]}_page_{page_number + 1}.png"
            )


            # Convert PDF page to image
            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(2, 2)
            )


            pixmap.save(
                output_path
            )


            pages.append(
                output_path
            )


        total_pages = len(pages)

        pdf.close()


        return {
            "file_type": "pdf",
            "pages": pages,
            "total_pages": total_pages
        }