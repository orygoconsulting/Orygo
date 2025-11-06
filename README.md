# Orygo Consulting – Ops Consultant SaaS

**Ops Consultant** es un SaaS desarrollado por **Orygo Consulting** que actúa como un **consultor digital de operaciones**.  
Analiza datos de producción directamente desde Google Sheets y responde preguntas con inteligencia artificial, aplicando metodologías específicas de operaciones industriales.

---

## 🚀 Características

- **Asistente de operaciones** con IA (usa datos reales de producción).  
- **Multi-tenant**: cada empresa tiene su propia hoja y API key.  
- **Conexión directa con Google Sheets**, sin subir archivos.  
- **Visualización de KPIs** (OEE, disponibilidad, rendimiento, calidad).  
- **Ingesta de documentos (PDF, TXT)** para ampliar conocimiento.  
- 100 % en la nube — sin instalaciones locales.

---

## ⚙️ Stack principal

| Componente | Tecnología |
|-------------|-------------|
| Backend | FastAPI + Uvicorn |
| LLM & Embeddings | OpenAI (gpt-4o-mini, text-embedding-3-small) |
| Vector DB | Pinecone (namespace por empresa) |
| Datos fuente | Google Sheets (gspread + google-auth) |
| Automatización | Polling task (cron) |
| Despliegue | Docker + Render |
| Lenguaje | Python 3.11 |

---

## 🔹 Endpoints principales

### `POST /chat`
Consulta al asistente con tu API key y empresa:
```json
{
  "question": "¿Cuál fue el OEE promedio la última semana?"
}
