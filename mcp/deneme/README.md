# Node.js MCP Örneği

Bu depo, Node.js kullanarak basit bir MCP (Model Context Protocol) sunucusu örneği içerir. Sunucu stdio üzerinden çalışır ve iki örnek araç (tool) ile iki örnek kaynak (resource) sağlar.

## Kurulum

1. Bağımlılıkları kurun:

```bash
npm install
```

2. Geliştirme modunda çalıştırın:

```bash
npm run dev
```

veya normal çalıştırma:

```bash
npm start
```

> MCP istemcileri (örn. Cursor, Claude Desktop veya başka bir MCP uyumlu istemci) bu sunucuyu stdio üzerinden başlatmalıdır. `node server.js` komutu yeterlidir.

## Sağlanan Özellikler

- Tools
  - `hello` (argüman: `name: string`) → "Merhaba, <name>!"
  - `time` (argüman yok) → geçerli ISO tarih/saat
- Resources
  - `res://giris` → düz metin giriş açıklaması
  - `res://durum` → basit JSON durum verisi

## İstemci Entegrasyonu (Örnek)
Bir MCP istemcisinde şu şekilde tanımlayabilirsiniz (uygulamaya göre değişir):

```json
{
  "name": "node-mcp-ornek",
  "command": "node",
  "args": ["server.js"],
  "env": {}
}
```

## Lisans
MIT
