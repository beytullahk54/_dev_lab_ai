import 'dotenv/config';
import { GoogleGenAI } from '@google/genai';

const apiKey = process.env.GOOGLE_API_KEY;
if (!apiKey) {
  console.error('GOOGLE_API_KEY .env dosyasında bulunamadı. Lütfen anahtarı ekleyin.');
  process.exit(1);
}

async function run() {
  const ai = new GoogleGenAI({ apiKey });

  const result = await ai.models.generateContent({
    model: 'gemini-2.5-flash',
    contents: 'Merhaba Gemini! Bana kısaca kendini tanıtır mısın?'
  });

  
  console.log('\n--- Yanıt ---\n');
  console.log(result.text);
}
run().catch(console.error);
