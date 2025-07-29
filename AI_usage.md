# AI Usage Summary

This document outlines how AI tools — specifically large language models — were used during the development of the **Dark Souls Lore Knowledge Graph** project.

---

## Purpose of AI Integration

The Dark Souls universe is known for its indirect storytelling and fragmented lore, conveyed through item descriptions and dialogue. To reconstruct this narrative into a structured knowledge graph, I used AI to:

- Extract meaningful **entities** (characters, locations, items, covenants)
- Identify **relationships** (e.g., created_by, affiliated_with, found_in)
- Convert natural language into **triplets** (subject, predicate, object) for Neo4j

---

## AI Tooling Used

### OpenAI GPT-4
- **Model:** `gpt-4o`
- **Interface:** `openai>=1.0.0` Python SDK
- **Used for:**
  - Converting freeform in-game item descriptions into clean structured triples
  - Interpreting complex lore references and resolving ambiguous phrasing
  - Batch-processing item, spell, and weapon descriptions at scale

###  ChatGPT (as a coding assistant)
- **Used for:**
  - Planning the pipeline for scraping → parsing → extraction → graph modeling
  - Designing the Cypher-ready triple format
  - Debugging JSON parsing and environment handling


---

## Example of Prompt Used

```plaintext
You are a Dark Souls lore extraction assistant. Given a weapon's name, description, and availability, extract a list of factual (subject, predicate, object) triples related to lore.

Avoid gameplay effects or stats. Focus only on:
- who created or used the weapon
- origin location or affiliations
- related characters or factions

Format:
[
  (subject, predicate, object),
  ...
]
```
---

## Effectiveness
GPT-4 was particularly useful in:
- Inferring lore-linked relationships
- Parsing nuanced and often ambiguous item descriptions
- Keeping output consistently structured for downstream graph loading

## Safety
All API keys were securely handled using:
- .env for local development
- .gitignore to prevent key leaks

---

## Conclusion
AI tools were essential for converting narrative game data into a structured, queryable graph. This project demonstrates how LLMs can meaningfully bridge the gap between story-rich natural language and structured semantic knowledge.

