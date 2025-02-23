# Tater - A Discord Bot Powered by EXO AI Cluster (WIP)

Tater is a Discord bot that uses EXO for chat functionality and tool integration while still using Ollama for embedding generation.

## Overview

- **Chat & Tools:**  
  Tater leverages EXO's ChatGPT-compatible API to process messages and execute various tool functions such as:
  - YouTube video summarization
  - Web article summarization and web search
  - Image generation
  - Premiumize integration (download and torrent processing)
  - RSS feed monitoring and management

- **Embeddings:**  
  The bot uses Ollama for generating embeddings, which are used to store and retrieve conversation context.

## Setup

1. **Environment Variables:**  
   Create a `.env` file in the project root with the following variables:

   ```dotenv
   # EXO (Chat API) settings
   EXO_API_ENDPOINT=http://<your-exo-ip>:52415
   EXO_MODEL=llama-3.1-8b
   EXO_TEMPERATURE=0.7

   # Ollama (Embeddings) settings
   OLLAMA_HOST=10.4.20.204
   OLLAMA_PORT=11434
   OLLAMA_EMB_MODEL=nomic-embed-text

   # Other settings
   CONTEXT_LENGTH=10000
   DISCORD_TOKEN=<your-discord-bot-token>
   ADMIN_USER_ID=<your-admin-user-id>
```
