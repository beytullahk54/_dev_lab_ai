"""
LoRA Eğitimi - Apple Silicon için Minimal Örnek (DÜZELTİLDİ ✅)
1B model ile basit eğitim
"""

import torch
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling  # <--- YENİ: Bunu ekledik
)
from peft import LoraConfig, get_peft_model
from datasets import Dataset

print("\n" + "="*60)
print("🍎 LoRA EĞİTİMİ - Apple Silicon (Fixed)")
print("="*60 + "\n")

# ============================================
# ADIM 1: CİHAZ KONTROLÜ
# ============================================
print("📱 ADIM 1: Cihaz kontrol ediliyor...")

if torch.backends.mps.is_available():
    device = "mps"  # Apple GPU
    print("   ✅ Apple GPU (MPS) aktif!\n")
else:
    device = "cpu"
    print("   ⚠️  CPU kullanılacak (daha yavaş)\n")

# ============================================
# ADIM 2: MODEL YÜKLEME
# ============================================
print("📦 ADIM 2: Model yükleniyor...")
print("   Model: TinyLlama-1.1B")

# Model: Qwen2.5-1.5B (Türkçe desteği ÇOK daha iyi)
model_name = "Qwen/Qwen2.5-1.5B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token  # Padding token ayarla

# Model yükle
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float32,  # Apple için en stabil
)
model = model.to(device)

print("   ✅ Model yüklendi (~1.1B parametre)\n")

# ============================================
# ADIM 3: LORA UYGULA
# ============================================
print("🔧 ADIM 3: LoRA uygulanıyor...")
print("   LoRA nedir? Modelin sadece küçük bir kısmını eğitir")
print("   Normal: 1.1 milyar parametre eğitilir")
print("   LoRA ile: Sadece ~2 milyon parametre eğitilir!")

lora_config = LoraConfig(
    r=8,              # LoRA rank (ne kadar küçükse o kadar az parametre)
    lora_alpha=16,    # Scaling factor
    target_modules=["q_proj", "v_proj"],  # Hangi katmanlar eğitilecek
    lora_dropout=0.05,
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

print("\n   📊 Parametre İstatistikleri:")
model.print_trainable_parameters()
print()

# ============================================
# ADIM 4: EĞİTİM VERİSİ
# ============================================
print("📚 ADIM 4: Eğitim verisi hazırlanıyor...")

# Basit Türkçe örnekler
# Daha Kaliteli ve Yapılı Veri Seti
# Modelin "Soru -> Cevap" ilişkisini kurabilmesi için formatlı veri kullanıyoruz.
train_data = [
    "Soru: Merhaba.\nCevap: Merhaba! Size nasıl yardımcı olabilirim?",
    "Soru: Nasılsın?\nCevap: Teşekkür ederim, iyiyim. Siz nasılsınız?",
    "Soru: Python nedir?\nCevap: Python, öğrenmesi kolay ve çok popüler bir programlama dilidir.",
    "Soru: Türkiye'nin başkenti neresidir?\nCevap: Türkiye'nin başkenti Ankara'dır.",
    "Soru: İstanbul'un nüfusu kaçtır?\nCevap: İstanbul, Türkiye'nin en kalabalık şehridir.",
    "Soru: Yapay zeka nedir?\nCevap: Yapay zeka, bilgisayarların insan gibi düşünmesini sağlayan teknolojidir.",
    "Soru: LoRA ne işe yarar?\nCevap: LoRA, büyük yapay zeka modellerini çok daha az bellek ve işlem gücüyle eğitmemizi sağlar.",
    "Soru: Apple Silicon (M1/M2) iyi midir?\nCevap: Evet, Apple Silicon işlemciler hem çok hızlıdır hem de çok az enerji tüketir.",
    "Soru: Derin öğrenme nedir?\nCevap: Derin öğrenme, insan beynindeki sinir ağlarını taklit eden bir yapay zeka yöntemidir.",
    "Soru: En iyi programlama dili hangisi?\nCevap: Projeye göre değişir ama Python, JavaScript ve C++ en popüler dillerdendir.",
    "Soru: Yazılım öğrenmek zor mu?\nCevap: Başlarda zorlayıcı olabilir ama sabır ve pratikle herkes yazılım öğrenebilir.",
    "Soru: Bugün hava nasıl?\nCevap: Ben bir yapay zekayım, dünyadaki hava durumunu göremem ama umarım hava güzeldir.",
    "Soru: Bana bir fıkra anlat.\nCevap: Temel bir gün... Şaka şaka, ben daha çok teknik konularda yardımcı olabilirim.",
    "Soru: Bilgisayar nedir?\nCevap: Bilgisayar, verileri işleyen ve saklayan elektronik bir cihazdır.",
    "Soru: İnternet nasıl çalışır?\nCevap: İnternet, dünya genelindeki bilgisayarların birbirine kablolar ve sinyallerle bağlandığı dev bir ağdır."
]

print(f"   ✅ {len(train_data)} örnek hazırlandı\n")

# Dataset oluştur ve tokenize et
dataset = Dataset.from_dict({"text": train_data})

def tokenize(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        max_length=128,
        # padding burada yapmıyoruz, DataCollator yapacak
    )

tokenized_dataset = dataset.map(tokenize, batched=True)

# <--- YENİ: Data Collator (Labels/Cevap Anahtarı oluşturur)
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, 
    mlm=False  # Masked Language Modeling değil, Causal LM yapıyoruz
)

print(f"   ✅ {len(train_data)} örnek hazırlandı\n")

# ============================================
# ADIM 5: EĞİTİM AYARLARI
# ============================================
print("⚙️  ADIM 5: Eğitim ayarları yapılıyor...")

training_args = TrainingArguments(
    output_dir="./lora-model",           # Model nereye kaydedilecek
    num_train_epochs=10,                  # Daha iyi öğrenmesi için artırdık (3 -> 10)
    per_device_train_batch_size=2,       # Aynı anda kaç örnek
    learning_rate=2e-4,                   # Öğrenme hızı
    logging_steps=1,                      # Her adımda log göster
    save_steps=50,                        # Her 50 adımda kaydet
    save_total_limit=1,                   # Sadece en iyi modeli sakla
    report_to="none",                     # Logları gösterme
    dataloader_pin_memory=False,          # Apple hatasını önlemek için
)

# ============================================
# ADIM 6: EĞİTİM
# ============================================
print("🎓 ADIM 6: Eğitim başlıyor...")
print("   ⏱️  Tahmini süre: 2-5 dakika\n")
print("-" * 60)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator, # <--- YENİ: Collator'ı ekledik
)

# EĞİTİMİ BAŞLAT!
trainer.train()

print("-" * 60)
print("\n   ✅ Eğitim tamamlandı!\n")

# ============================================
# ADIM 7: MODELİ KAYDET
# ============================================
print("💾 ADIM 7: Model kaydediliyor...")

model.save_pretrained("./lora-model")
tokenizer.save_pretrained("./lora-model")

print("   ✅ Model kaydedildi: ./lora-model\n")

# ============================================
# ADIM 8: TEST
# ============================================
print("🧪 ADIM 8: Hızlı test yapılıyor...\n")

model.eval()
test_prompt = "Merhaba!"

inputs = tokenizer(test_prompt, return_tensors="pt").to(device)

with torch.no_grad():
    outputs = model.generate(
        **inputs, 
        max_new_tokens=30, 
        temperature=0.7,
        do_sample=True,
        pad_token_id=tokenizer.pad_token_id
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

print(f"   Prompt: {test_prompt}")
print(f"   Yanıt: {response}\n")

# ============================================
# BİTİŞ
# ============================================
print("="*60)
print("🎉 TAMAMLANDI!")
print("="*60)
print("\n📁 Oluşturulan dosyalar:")
print("   • ./lora-model/  (Eğitilmiş model)")
print("\n🚀 Sonraki adımlar:")
print("   • Modeli test et: python test.py")
print("   • Daha fazla veri ekle ve tekrar eğit")
print("\n💡 LoRA'yı öğrendiniz!")
print("   • Sadece 2M parametre eğittiniz (1.1B yerine)")
print("   • %99.8 daha az bellek kullandınız")
print("   • Çok daha hızlı eğittiniz")
print("="*60 + "\n")
