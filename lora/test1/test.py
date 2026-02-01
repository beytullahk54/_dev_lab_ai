"""
Eğitilmiş LoRA Modelini Test Et
İnteraktif sohbet modu
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

print("\n" + "="*60)
print("🤖 MODEL TEST - İnteraktif Mod")
print("="*60 + "\n")

# Cihaz kontrolü
if torch.backends.mps.is_available():
    device = "mps"
    print("✅ Apple GPU aktif\n")
else:
    device = "cpu"
    print("⚠️  CPU kullanılıyor\n")

# Model yükle
print("📦 Model yükleniyor...")

base_model = "Qwen/Qwen2.5-1.5B-Instruct"
lora_model = "./lora-model"

tokenizer = AutoTokenizer.from_pretrained(base_model)
model = AutoModelForCausalLM.from_pretrained(
    base_model,
    torch_dtype=torch.float32
)

# LoRA adapter'ı yükle
model = PeftModel.from_pretrained(model, lora_model)
model = model.to(device)
model.eval()

print("✅ Model hazır!\n")
print("="*60)
print("💬 Sohbet başladı! (Çıkmak için 'q' yazın)")
print("="*60 + "\n")

# İnteraktif döngü
while True:
    prompt = input("👤 Siz: ")
    
    if prompt.lower() in ['q', 'quit', 'exit', 'çık']:
        print("\n👋 Görüşmek üzere!\n")
        break
    
    if not prompt.strip():
        continue
    
    # Model'e formatlı sor (Prompt Template)
    # Model bu formatta eğitildiği için, formatı ona hatırlatıyoruz.
    full_prompt = f"Soru: {prompt}\nCevap:"
    
    inputs = tokenizer(full_prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=50,      # Cevap çok uzamasın
            temperature=0.5,        # Daha tutarlı olsun (0.7 -> 0.5)
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.2  # Aynı şeyi tekrarlamasını engelle
        )
    
    # Sadece cevabı al (Soruyu ve prompt'u kes)
    full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Çıktıdan sadece "Cevap:" sonrasını ayıkla
    if "Cevap:" in full_response:
        response = full_response.split("Cevap:")[-1].strip()
    else:
        response = full_response
        
    print(f"🤖 Model: {response}\n")
