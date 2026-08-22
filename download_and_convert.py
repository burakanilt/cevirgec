import urllib.request
import tarfile
import os
import subprocess

os.makedirs('assets/models/turkish_rec', exist_ok=True)

# Download PaddleOCR Turkish inference model
url = "https://paddleocr.bj.bcebos.com/PP-OCRv3/multilingual/turkish_PP-OCRv3_rec_infer.tar"
tar_path = "assets/models/turkish_PP-OCRv3_rec_infer.tar"

print("Downloading Turkish PP-OCRv3 model...")
urllib.request.urlretrieve(url, tar_path)

print("Extracting...")
with tarfile.open(tar_path, 'r') as tar:
    tar.extractall("assets/models/turkish_rec")

# Convert to ONNX
model_dir = "assets/models/turkish_rec/turkish_PP-OCRv3_rec_infer"
onnx_path = "assets/models/turkish_PP-OCRv3_rec_infer.onnx"

print("Converting to ONNX using paddle2onnx...")
cmd = [
    ".\\.venv\\Scripts\\paddle2onnx.exe",
    "--model_dir", model_dir,
    "--model_filename", "inference.pdmodel",
    "--params_filename", "inference.pdiparams",
    "--save_file", onnx_path,
    "--opset_version", "11",
    "--enable_onnx_checker", "True"
]

subprocess.run(cmd, check=True)
print(f"ONNX model saved to {onnx_path}")

# Now download the Turkish dictionary
dict_url = "https://raw.githubusercontent.com/PaddlePaddle/PaddleOCR/main/ppocr/utils/dict/turkish_dict.txt"
dict_path = "assets/models/turkish_dict.txt"
print("Downloading Turkish Dictionary...")
urllib.request.urlretrieve(dict_url, dict_path)

print("All done!")
