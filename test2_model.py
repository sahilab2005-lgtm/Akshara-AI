import os

MODEL_PATH = "./sarvam_local"

print("Exists:", os.path.exists(MODEL_PATH))
print("Tokenizer model exists:",
      os.path.exists(os.path.join(MODEL_PATH, "tokenizer.model")))