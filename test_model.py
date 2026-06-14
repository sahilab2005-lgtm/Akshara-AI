from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load local model
local_path = "./sarvam_local"

print("Loading local model...")

tokenizer = AutoTokenizer.from_pretrained(local_path)
model = AutoModelForCausalLM.from_pretrained(local_path)

print("Model loaded successfully!")


# TEXT GENERATION
prompt = "Answer only in English: What is Agentic AI?"

inputs = tokenizer(prompt, return_tensors="pt")

outputs = model.generate(
    **inputs,
    max_new_tokens=100,
    do_sample=True,
    temperature=0.7,
    pad_token_id=tokenizer.eos_token_id
)

response = tokenizer.decode(
    outputs[0],
    skip_special_tokens=True
)

print("\n===== TEXT GENERATION =====")
print(response)


# SUMMARIZATION
text_to_summarize = """
Artificial Intelligence is a branch of computer science that enables
machines to perform tasks that normally require human intelligence.
It includes machine learning, natural language processing, computer vision,
and robotics. AI is transforming industries such as healthcare,
finance, education, and transportation.
"""

summary_prompt = f"""
Summarize the following text in 2 lines:

{text_to_summarize}
"""

inputs = tokenizer(summary_prompt, return_tensors="pt")

outputs = model.generate(
    **inputs,
    max_new_tokens=100,
    do_sample=True,
    temperature=0.7,
    pad_token_id=tokenizer.eos_token_id
)

summary = tokenizer.decode(
    outputs[0],
    skip_special_tokens=True
)


print(summary)


# TRANSLATION
text_to_translate = """
Artificial Intelligence is transforming the world.
"""

translation_prompt = f"""
Translate the following text to Hindi:

{text_to_translate}
"""

inputs = tokenizer(translation_prompt, return_tensors="pt")

outputs = model.generate(
    **inputs,
    max_new_tokens=100,
    do_sample=True,
    temperature=0.7,
    pad_token_id=tokenizer.eos_token_id
)

translation = tokenizer.decode(
    outputs[0],
    skip_special_tokens=True
)

print("\n===== TRANSLATION =====")
print(translation)