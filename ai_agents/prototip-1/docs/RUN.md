# Çalıştırma

## Her Seferinde

```bash
cd /Volumes/Kodlooper/kodlooperYazilim/htdocs/ai_agents
source .venv/bin/activate
```

## Kullanım

```bash
# Tek atış
python agent.py "23 * 47 kaç eder?"

# REPL (interaktif)
python agent.py

# Model değiştir
python agent.py --model llama-3.3-70b-versatile "soru"

# Debug mod (tool çağrılarını gör)
python agent.py -v "soru"
```

## Geliştirme

```bash
# Kod değişikliği sonrası hızlı test
python3 -m py_compile agent.py
python agent.py -v "test"

# Yeni tool ekleme
# 1. tools/yeni.py oluştur
# 2. tools/__init__.py'ye kaydet
# 3. python agent.py -v "test"
```

## Örnekler

```bash
# Hesap + dosya yazma
python agent.py -v "2+2 kaç eder ve sonucu result.txt'ye yaz"

# Web arama
python agent.py "Python 3.12 yeniliklerini araştır"

# URL'den veri çek
python agent.py "https://example.com başlığı nedir?"
```

## Alias (Kısayol)

```bash
# ~/.zshrc veya ~/.bashrc
echo "alias aiagent='cd /Volumes/Kodlooper/kodlooperYazilim/htdocs/ai_agents && source .venv/bin/activate && python agent.py'" >> ~/.zshrc
source ~/.zshrc

# Kullanım
aiagent "23*47 kaç?"
```
