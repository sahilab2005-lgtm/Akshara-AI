import os

MODEL_PATH = "./sarvam_local"

print("Exists:", os.path.exists(MODEL_PATH))
print("\nFiles:")

for f in os.listdir(MODEL_PATH):
    print("-", f)