# Claude API — Referencia Técnica
> Guía de referencia para el Claude Impact Lab Chile 2026.  
> Todas las APIs verificadas contra `@anthropic-ai/sdk` versión actual.

---

## Setup básico

```bash
npm install @anthropic-ai/sdk
```

```typescript
import Anthropic from '@anthropic-ai/sdk'

const client = new Anthropic() // lee ANTHROPIC_API_KEY del entorno

const response = await client.messages.create({
  model: 'claude-sonnet-4-6',
  max_tokens: 1024,
  messages: [{ role: 'user', content: 'Hola, ¿cómo estás?' }],
})

for (const block of response.content) {
  if (block.type === 'text') console.log(block.text)
}
```

---

## Tool Use — la base de todo agente

Claude puede llamar funciones (tools) que tú defines. El patrón: tú le pasas herramientas → Claude decide cuándo usarlas → tú ejecutas → le devuelves el resultado. `betaZodTool` + `toolRunner` automatizan el loop completo.

```bash
npm install zod
```

```typescript
import { betaZodTool } from '@anthropic-ai/sdk/helpers/beta/zod'
import { z } from 'zod'

// Ejemplo conectado a Alerta Cuenta
const clasificarFraude = betaZodTool({
  name: 'classify_fraud',
  description: 'Clasifica el tipo de fraude financiero descrito por el usuario',
  inputSchema: z.object({
    description: z.string().describe('Relato de la víctima en sus propias palabras'),
    institution: z.string().optional().describe('Banco o fintech involucrada'),
  }),
  run: async ({ description, institution }) => {
    const res = await fetch('/api/ai/classify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description, additional_context: { institution } }),
    })
    return JSON.stringify(await res.json())
  },
})

const final = await client.beta.messages.toolRunner({
  model: 'claude-sonnet-4-6',
  max_tokens: 2048,
  max_iterations: 10,   // evita loops infinitos en producción
  tools: [clasificarFraude],
  messages: [{ role: 'user', content: 'Me llegó un SMS de mi banco con un link...' }],
})

console.log(final.content)
```

`toolRunner` ejecuta el loop completo: Claude llama la tool → corre tu `run` → le devuelve el resultado → Claude continúa hasta tener la respuesta final.

---

## Streaming — respuestas token a token

```typescript
const stream = client.messages.stream({
  model: 'claude-sonnet-4-6',
  max_tokens: 4096,
  messages: [{ role: 'user', content: 'Explica qué es el smishing' }],
})

for await (const event of stream) {
  if (
    event.type === 'content_block_delta' &&
    event.delta.type === 'text_delta'
  ) {
    process.stdout.write(event.delta.text)
  }
}

const finalMessage = await stream.finalMessage()
```

---

## Extended Thinking — razonamiento profundo

Opus 4.7 y Sonnet 4.6 pueden razonar antes de responder. Ideal para análisis de casos complejos, evaluación regulatoria, debugging.

### Modo estándar (control explícito)

```typescript
const response = await client.messages.create({
  model: 'claude-opus-4-7',
  max_tokens: 16000,
  thinking: {
    type: 'enabled',
    budget_tokens: 8000,  // cuántos tokens puede "pensar" antes de responder
  },
  messages: [{ role: 'user', content: 'Analiza este caso de fraude paso a paso...' }],
})

// El thinking aparece como bloque separado — muéstralo en la demo
for (const block of response.content) {
  if (block.type === 'thinking') {
    console.log('🧠 Razonamiento interno:\n', block.thinking)
  } else if (block.type === 'text') {
    console.log('💬 Respuesta:\n', block.text)
  }
}
```

### Modo adaptativo (el modelo decide cuánto pensar)

```typescript
await client.messages.create({
  model: 'claude-opus-4-7',
  max_tokens: 16000,
  thinking: {
    type: 'adaptive',
    display: 'summarized',   // 'summarized' | 'none' | 'show'
  },
  output_config: {
    effort: 'high',          // 'low' | 'medium' | 'high' | 'max'
  },
  messages: [{ role: 'user', content: 'Resuelve paso a paso...' }],
})
```

> **Tip demo:** Mostrar el bloque `thinking` al jurado es muy efectivo — demuestra que Claude razona antes de clasificar un fraude, no solo pattern-matching.

---

## Claude Agent SDK — agentes completos en 10 líneas

El Claude Agent SDK es el runtime oficial de Anthropic para construir agentes. Es el mismo motor que usa Claude Code. Trae tools built-in (bash, read, write, edit, glob, grep, web_fetch, web_search), soporta MCP, y maneja sesiones y permisos.

```bash
npm install @anthropic-ai/claude-agent-sdk
```

```typescript
import { query } from '@anthropic-ai/claude-agent-sdk'

for await (const message of query({
  prompt: '¿Qué archivos hay en la carpeta actual? Resume qué hace cada uno.',
})) {
  console.log(message)
}
```

**Qué te da gratis:**
- Tools built-in: bash, edición de archivos, búsqueda web, fetch
- Sesiones persistentes — el agente recuerda turnos anteriores
- Permisos finos — decides qué tools puede usar y cuándo pedir confirmación
- Hooks `PreToolUse` / `PostToolUse` para auditar o modificar llamadas
- Outputs estructurados con Zod
- Adaptive thinking integrado

Docs: https://code.claude.com/docs/en/agent-sdk/typescript

---

## MCP — Model Context Protocol

MCP es el estándar abierto (impulsado por Anthropic) para conectar modelos a datos y sistemas externos. "USB-C para IA": escribes un servidor que expone tools, resources y prompts, y cualquier cliente MCP (Claude Desktop, Claude Code, Cursor, VS Code) puede usarlo.

```bash
npm install @modelcontextprotocol/sdk zod
```

```typescript
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import { z } from 'zod'

// Ejemplo: servidor MCP para Alerta Cuenta
const server = new McpServer({ name: 'alerta-cuenta', version: '1.0.0' })

server.tool(
  'consulta_estado_caso',
  'Consulta el estado de un caso de fraude por código de seguimiento',
  { tracking_code: z.string() },
  async ({ tracking_code }) => ({
    content: [{ type: 'text', text: `Estado del caso ${tracking_code}: en revisión` }],
  }),
)

await server.connect(new StdioServerTransport())
```

Úsalo si tu producto expone datos específicos (registro CMF, circulares SII, datasets propios) y quieres que Claude los consulte con reglas tuyas. Docs: https://modelcontextprotocol.io

---

## Prompt Caching — ahorra hasta 90% en contexto repetido

Si tu agente usa un system prompt largo (instrucciones + dataset), el prompt caching guarda ese prefijo y cobra ~0.1× por lecturas posteriores.

```typescript
await client.messages.create({
  model: 'claude-opus-4-7',
  max_tokens: 2048,
  system: [
    {
      type: 'text',
      text: '...system prompt largo con instrucciones y contexto...',
      cache_control: { type: 'ephemeral', ttl: '1h' },  // TTL extendido
      // sin ttl → usa el default de 5 minutos: cache_control: { type: 'ephemeral' }
    },
  ],
  messages: [{ role: 'user', content: 'Pregunta del usuario' }],
})
```

**Reglas clave:**
- Mínimo 2048 tokens cacheables en Sonnet 4.6 (4096 en Opus / Haiku)
- TTL válidos: `'5m'` (default) o `'1h'`
- Máximo 4 breakpoints por request
- Verifica hits: `response.usage.cache_read_input_tokens > 0`
- Cualquier byte que cambie en el prefijo invalida todo lo posterior — pon contenido estable primero

Docs: https://platform.claude.com/docs/en/build-with-claude/prompt-caching

---

## Imágenes y PDFs

### Imagen por URL

```typescript
messages: [{
  role: 'user',
  content: [
    { type: 'image', source: { type: 'url', url: 'https://...' } },
    { type: 'text', text: '¿Qué dice este comprobante de transferencia?' },
  ],
}]
```

### PDF con Files API (recomendado si lo reutilizas)

```typescript
import { toFile } from '@anthropic-ai/sdk'
import fs from 'fs'

const uploaded = await client.beta.files.upload({
  file: await toFile(
    fs.createReadStream('circular-cmf.pdf'),
    undefined,
    { type: 'application/pdf' },
  ),
  betas: ['files-api-2025-04-14'],
})

await client.beta.messages.create({
  model: 'claude-opus-4-7',
  max_tokens: 4096,
  messages: [{
    role: 'user',
    content: [
      { type: 'text', text: 'Resume esta circular CMF' },
      {
        type: 'document',
        source: { type: 'file', file_id: uploaded.id },
        citations: { enabled: true },
      },
    ],
  }],
  betas: ['files-api-2025-04-14'],
})
```

---

## Prompt Engineering — lo que funciona

```
Eres analista de fraudes financieros ciudadano en Chile. Tu tarea es evaluar
el relato de una víctima e identificar el tipo de fraude, acciones urgentes
y documentación requerida.

Devuelve SOLO este JSON:
{
  "fraud_type": "phishing|vishing|smishing|whatsapp_impersonation|...",
  "confidence": "high|medium|low",
  "urgent_actions": ["Acción 1", "Acción 2"],
  "missing_info": ["Dato faltante 1"]
}

RESTRICCIONES:
- Nunca inventes leyes ni artículos específicos
- Si falta información crítica, devuelve needs_clarification: true
- La primera línea de tu respuesta debe ser { y la última }
```

**Patrones efectivos:**
1. Rol + tarea explícita en el system prompt
2. Schema JSON exacto esperado (no "devuelve JSON", sino el schema completo)
3. Ejemplos few-shot cuando el patrón es complejo
4. Restricciones explícitas (qué NO debe hacer)
5. XML tags para estructurar input: `<relato>`, `<contexto>`
6. `budget_tokens` activado para análisis que requieren razonamiento

---

## Stacks recomendados

| Capa | Recomendado | Alternativa |
|------|------------|-------------|
| **Frontend** | Next.js 14+ (App Router) | React + Vite |
| **Backend** | FastAPI (Python) · Express (Node) | Hono · Fastify |
| **DB + Auth** | Supabase (Postgres + pgvector + Storage) | Firebase · Neon |
| **Deploy** | Railway · Fly.io (si necesitas workers) | Vercel (Next.js), Render |
| **IA** | Claude API + `@anthropic-ai/sdk` | — |
| **Agentes** | Claude Agent SDK | LangGraph |
| **Integraciones** | MCP SDK | REST directo |

---

## Supabase en 5 minutos

```bash
npm install @supabase/supabase-js @supabase/ssr
```

```typescript
// src/lib/supabase/client.ts
import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  )
}
```

```typescript
// Auth con magic link
const supabase = createClient()
await supabase.auth.signInWithOtp({
  email: 'user@ejemplo.cl',
  options: { emailRedirectTo: `${origin}/callback` },
})
```

> **Row Level Security es obligatoria desde el día uno** — nunca uses `service_role` en rutas públicas.

---

## RAG con pgvector — resumen

Si tu producto necesita buscar en muchos documentos:

1. **Ingesta:** divide docs en chunks de ~500 tokens
2. **Embeddings:** convierte chunks a vectores (`text-embedding-3-small`)
3. **Storage:** guarda vectores + texto en pgvector (Supabase lo soporta nativo)
4. **Query:** embedding del query → similarity search → top-k chunks → pasar a Claude como contexto

---

## Deploy rápido

```bash
npm install -g vercel
vercel
```

Conectas tu repo, configuras env vars (`ANTHROPIC_API_KEY`, `NEXT_PUBLIC_SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`), listo. CI/CD automático en cada push.

---

## Recursos imprescindibles

| Recurso | URL |
|---------|-----|
| Anthropic Docs | https://docs.anthropic.com |
| Claude Agent SDK | https://code.claude.com/docs/en/agent-sdk/typescript |
| Anthropic Cookbook | https://github.com/anthropics/anthropic-cookbook |
| Claude Code | https://claude.ai/code |
| MCP spec + servers | https://modelcontextprotocol.io |
| Supabase docs | https://supabase.com/docs |
| Next.js App Router | https://nextjs.org/docs/app |
| Vercel | https://vercel.com/docs |
