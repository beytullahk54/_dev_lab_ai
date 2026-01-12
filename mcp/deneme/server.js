import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/transport/stdio.js";
import {
	ListToolsRequestSchema,
	CallToolRequestSchema,
	ListResourcesRequestSchema,
	ReadResourceRequestSchema
} from "@modelcontextprotocol/sdk/types.js";

// Basit Node.js MCP sunucusu (stdio üzerinden)
const server = new Server(
	{ name: "node-mcp-ornek", version: "0.1.0" },
	{
		capabilities: {
			// Araçlar (tools) listelenebiliyor
			tools: {},
			// Kaynaklar (resources) listelenebiliyor
			resources: {},
		},
	}
);

// 1) Tools: hello ve time araçlarını tanımlayalım
server.setRequestHandler(ListToolsRequestSchema, async () => {
	return {
		tools: [
			{
				name: "hello",
				description: "Merhaba diyen basit araç. Argüman olarak name alır.",
				inputSchema: {
					type: "object",
					properties: { name: { type: "string" } },
					required: ["name"],
				},
			},
			{
				name: "time",
				description: "ISO tarih/saat döndürür. Argüman almaz.",
				inputSchema: { type: "object", properties: {} },
			},
		],
	};
});

server.setRequestHandler(CallToolRequestSchema, async (req) => {
	const { name: toolName, arguments: args } = req.params;

	if (toolName === "hello") {
		const inputName = typeof args?.name === "string" ? args.name : "Dünya";
		return {
			content: [
				{ type: "text", text: `Merhaba, ${inputName}!` },
			],
		};
	}

	if (toolName === "time") {
		const now = new Date().toISOString();
		return {
			content: [
				{ type: "text", text: now },
			],
		};
	}

	throw new Error(`Bilinmeyen tool: ${toolName}`);
});

// 2) Resources: sabit bir metin kaynağı ve basit bir JSON kaynağı
const resources = [
	{
		uri: "res://giris",
		name: "Giriş Metni",
		description: "Basit bir tanıtım metni",
		mimeType: "text/plain",
		getContent: async () => "Bu, Node.js ile örnek bir MCP sunucusudur.",
	},
	{
		uri: "res://durum",
		name: "Durum JSON",
		description: "Sunucunun basit durum bilgisi",
		mimeType: "application/json",
		getContent: async () => JSON.stringify({ ok: true, ts: Date.now() }, null, 2),
	},
];

server.setRequestHandler(ListResourcesRequestSchema, async () => {
	return {
		resources: resources.map(r => ({
			uri: r.uri,
			name: r.name,
			description: r.description,
			mimeType: r.mimeType,
		})),
	};
});

server.setRequestHandler(ReadResourceRequestSchema, async (req) => {
	const targetUri = req.params.uri;
	const res = resources.find(r => r.uri === targetUri);
	if (!res) {
		throw new Error(`Kaynak bulunamadı: ${targetUri}`);
	}
	const body = await res.getContent();
	return {
		contents: [
			{
				uri: res.uri,
				mimeType: res.mimeType,
				text: typeof body === "string" ? body : undefined,
				raw: typeof body === "string" ? undefined : Buffer.from(String(body)).toString("base64"),
			},
		],
	};
});

// Sunucuyu stdio üzerinden başlat
const transport = new StdioServerTransport();
await server.connect(transport);
