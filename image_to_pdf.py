import os
from PIL import Image
import subprocess
import shutil

# Supported image formats
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp")

# Optional HEIC support (install pillow-heif first)
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    IMAGE_EXTENSIONS += (".heic", ".heif")
except:
    pass


def convert_image_to_pdf(img_path, out_path):
    img = Image.open(img_path)

    # Fix alpha channels
    if img.mode in ("RGBA", "LA"):
        img = img.convert("RGB")

    img.save(out_path, "PDF", resolution=100.0)
    print(f"✔ Converted: {img_path} → {out_path}")


def convert_folder_images_to_pdfs(folder_path, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(folder_path, "pdf_output")

    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(IMAGE_EXTENSIONS):
            full_path = os.path.join(folder_path, filename)
            base = os.path.splitext(filename)[0]
            pdf_path = os.path.join(output_dir, base + ".pdf")
            convert_image_to_pdf(full_path, pdf_path)

    print("\n✔ All images converted successfully.")
    print(f"Output folder: {output_dir}")


def merge_images_to_single_pdf(folder_path, output_pdf="merged.pdf"):
    images = []

    for filename in sorted(os.listdir(folder_path)):
        if filename.lower().endswith(IMAGE_EXTENSIONS):
            img = Image.open(os.path.join(folder_path, filename))

            if img.mode in ("RGBA", "LA"):
                img = img.convert("RGB")

            images.append(img)

    if not images:
        print("No images found to merge.")
        return

    first_img = images[0]
    rest_imgs = images[1:]

    first_img.save(output_pdf, "PDF", resolution=100.0, save_all=True, append_images=rest_imgs)
    print(f"\n✔ Merged {len(images)} images → {output_pdf}")


# Add DOCX support
DOCX_EXTENSIONS = (".docx",)


def convert_docx_to_pdf(docx_path, out_path):
    """
    Try docx2pdf first (requires pip install docx2pdf and MS Word on Windows).
    Fallback to LibreOffice (soffice) if available.
    """
    try:
        from docx2pdf import convert
        # docx2pdf accepts file-to-file paths
        convert(docx_path, out_path)
        print(f"✔ Converted: {docx_path} → {out_path}")
        return
    except Exception:
        pass

    # Fallback: LibreOffice headless
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        print("Cannot convert DOCX → PDF: install docx2pdf (and MS Word) or LibreOffice (soffice).")
        return

    out_dir = os.path.dirname(os.path.abspath(out_path)) or os.getcwd()
    try:
        subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", out_dir, docx_path],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # LibreOffice writes <basename>.pdf into out_dir
        print(f"✔ Converted (libreoffice): {docx_path} → {out_path}")
    except Exception as e:
        print(f"Failed to convert {docx_path} → {out_path}: {e}")


def convert_folder_docx_to_pdfs(folder_path, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(folder_path, "pdf_output")

    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(DOCX_EXTENSIONS):
            full_path = os.path.join(folder_path, filename)
            base = os.path.splitext(filename)[0]
            pdf_path = os.path.join(output_dir, base + ".pdf")
            convert_docx_to_pdf(full_path, pdf_path)

    print("\n✔ All DOCX files converted successfully.")
    print(f"Output folder: {output_dir}")


# -------------------------
# Example Usage (manual)
# -------------------------
if __name__ == "__main__":
    folder = input("Enter folder path: ")

    print("\n1. Convert all images → individual PDFs")
    print("2. Merge all images → single PDF")
    print("3. Convert all .docx → individual PDFs")
    choice = input("\nChoose option (1/2/3): ")

    if choice == "1":
        convert_folder_images_to_pdfs(folder)
    elif choice == "2":
        output_pdf = input("Enter output PDF name (default merged.pdf): ").strip() or "merged.pdf"
        merge_images_to_single_pdf(folder, output_pdf)
    elif choice == "3":
        convert_folder_docx_to_pdfs(folder)
    else:
        print("Invalid choice.")