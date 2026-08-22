import urllib.request
import tarfile
import os
import subprocess

os.makedirs('assets/models/v5_latin_rec', exist_ok=True)

url = "https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/latin_PP-OCRv5_mobile_rec_infer.tar"
tar_path = "assets/models/latin_PP-OCRv5_mobile_rec_infer.tar"

print("Downloading V5 Latin PP-OCRv5 model...")
urllib.request.urlretrieve(url, tar_path)

print("Extracting...")
with tarfile.open(tar_path, 'r') as tar:
    tar.extractall("assets/models/v5_latin_rec")

# Convert to ONNX
model_dir = "assets/models/v5_latin_rec/latin_PP-OCRv5_mobile_rec_infer"
onnx_path = "assets/models/latin_PP-OCRv5_mobile_rec_infer.onnx"

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

# Now download the V5 Latin dictionary
dict_url = "https://raw.githubusercontent.com/PaddlePaddle/PaddleOCR/main/ppocr/utils/dict/ppocrv5_latin_dict.txt"
dict_path = "assets/models/ppocrv5_latin_dict.txt"
print("Downloading V5 Latin Dictionary...")
urllib.request.urlretrieve(dict_url, dict_path)

print("All done!")
