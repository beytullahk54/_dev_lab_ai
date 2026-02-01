"""
TEST BASE - Eğitilmemiş Model Testi
LoRA modelini YÜKLEMEDEN ham modelin nasıl cevap verdiğini test edin.
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

print("\n" + "="*60)
print("👶 TEST BASE - Eğitilmemiş Ham Model")
print("="*60 + "\n")

# Cihaz kontrolü
if torch.backends.mps.is_available():
    device = "mps"
    print("✅ Apple GPU aktif\n")
else:
    device = "cpu"
    print("⚠️  CPU kullanılıyor\n")

# Model yükle
print("📦 Ham model yükleniyor (TinyLlama-1.1B)...")
print("⚠️  Uyarı: Bu model LoRA adaptörünü KULLANMIYOR!")

model_name = "Qwen/Qwen2.5-1.5B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float32
)
model = model.to(device)
model.eval()

print("✅ Ham model hazır!\n")
print("="*60)
print("💬 Sohbet başladı! (Çıkmak için 'q' yazın)")
print("👉 Türkçe soru sorduğunuzda muhtemelen İngilizce cevap verecek veya saçmalayacaktır.")
print("="*60 + "\n")

# İnteraktif döngü
while True:
    prompt = input("👤 Siz (Ham Modele Soruyorsunuz): ")
    
    if prompt.lower() in ['q', 'quit', 'exit', 'çık']:
        print("\n👋 Görüşmek üzere!\n")
        break
    
    if not prompt.strip():
        continue
    
    # Model'e sor
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id  # Base model eos kullanır
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"🤖 Ham Model: {response}\n")
