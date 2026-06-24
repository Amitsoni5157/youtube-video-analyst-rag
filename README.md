# 🎥 YouTube Transcript to Notes Converter

A production-ready Streamlit application that extracts multi-lingual transcripts from YouTube videos and leverages Open-Source LLMs via **Groq Cloud** to generate highly contextual, concise bulleted summaries within a 250-word constraint.

---

## 🏗️ System Architecture & Workflow

```text
┌────────────────────────────────────────────────────────┐
│                   1. Ingestion Phase                   │
└────────────────────────────────────────────────────────┘
            [ User inputs YouTube URL ] 
                         │
                         ▼ (Regex / Standard String Splitting)
            [ Extract 11-Char Video ID ]
                         │
                         ▼ (Streamlit Real-time Preview)
            [ Fetch & Render Thumbnail Image ]
                         │
                         ▼ (YouTubeTranscriptApi Engine)
            [ Cascade Attempt: Try 'en' (English) Captions ]
                         │
              ┌──────────┴──────────┐
              ▼ (If 'en' Fails)     ▼ (If 'en' Succeeds)
         [ Fallback to 'hi' ]   [ Load Raw Transcript ]
              │                     │
              └──────────┬──────────┘
                         ▼
            [ Combine Chunk Lists into Single String ]
                         │
                         ▼ (Defensive Guardrail: Trim at 15,000 Chars)
            [ Context-Window Optimized Text ]
                         │
                         ▼
┌────────────────────────────────────────────────────────┐
│                   2. Execution Phase                   │
└────────────────────────────────────────────────────────┘
            [ Optimized Transcript Text + System Prompt ]
                         │
                         ▼
            [ Groq Cloud Client Endpoint ]
                         │
            ┌────────────┴────────────┐
            ▼ (Primary Route)         ▼ (Automatic Failover)
     [ llama-3.3-8b-instant ]   [ llama-3.3-70b-versatile ]
            │                         │
            └────────────┬────────────┘
                         ▼ (Factual Summary Generated)
            [ Streamlit UI Response Block ]
                         │
                         ▼
            [ Formatted Markdown Output Displayed ]