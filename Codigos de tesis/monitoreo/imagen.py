import fitz  # PyMuPDF
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
import os

# ================================
# SELECCIÓN DE ARCHIVO
# ================================
def seleccionar_archivo():
    root = tk.Tk()
    root.withdraw()

    archivo = filedialog.askopenfilename(
        title="Selecciona un PDF o imagen",
        filetypes=[
            ("PDF e Imágenes", "*.pdf *.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
            ("Todos los archivos", "*.*")
        ]
    )
    return archivo

# ================================
# MEJORA DE IMAGEN
# ================================
def mejorar_imagen(img, escala=2):
    h, w = img.shape[:2]

    # Aumentar resolución (2x)
    img_res = cv2.resize(
        img,
        (w * escala, h * escala),
        interpolation=cv2.INTER_LANCZOS4
    )

    # Unsharp Mask (realce de bordes)
    blur = cv2.GaussianBlur(img_res, (0, 0), sigmaX=1.0)
    sharpened = cv2.addWeighted(
        img_res, 1.5,
        blur, -0.5,
        0
    )

    return sharpened

# ================================
# PDF → IMAGEN (HOJA COMPLETA)
# ================================
def pdf_a_imagen(ruta_pdf, zoom=2):
    doc = fitz.open(ruta_pdf)
    page = doc[0]  # Primera página

    # Matriz de transformación (controla resolución)
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)

    img = np.frombuffer(pix.samples, dtype=np.uint8)
    img = img.reshape(pix.height, pix.width, pix.n)

    # Convertir a BGR para OpenCV
    if pix.n == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    else:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    return img

# ================================
# MAIN
# ================================
def main():
    ruta = seleccionar_archivo()

    if not ruta:
        print("No se seleccionó archivo.")
        return

    nombre, ext = os.path.splitext(ruta)

    print("Procesando archivo (página completa)...")

    if ext.lower() == ".pdf":
        img = pdf_a_imagen(ruta, zoom=2)  # rasterización
        resultado = mejorar_imagen(img, escala=2)
        salida = f"{nombre}_mejorado.jpg"
    else:
        img = cv2.imread(ruta)
        resultado = mejorar_imagen(img, escala=2)
        salida = f"{nombre}_mejorado{ext}"

    cv2.imwrite(salida, resultado, [cv2.IMWRITE_JPEG_QUALITY, 95])

    print("Archivo original:", ruta)
    print("Archivo procesado:", salida)
    print("Página completa rasterizada y mejorada")

if __name__ == "__main__":
    main()
