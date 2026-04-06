# Raggy Bot Current Delivery Summary

## Executive Summary
Raggy Bot is now a Thai-first TRL service that combines two capabilities:
- grounded TRL question answering from indexed documents
- deterministic multi-turn TRL assessment using a structured rule base

The product is no longer just a single-turn RAG assistant. It now includes intent routing, assessment state handling, follow-up questioning, and metadata-safe operational review.

## Current Capability Snapshot
- FastAPI backend with a single public endpoint: `POST /raggy/trl`
- JWT bearer auth with `RS256`
- role-based retrieval separation for `admin` and `researcher`
- deterministic TRL rule base for levels 1-9
- session-aware assessment flow
- Thai-first fallback and follow-up messaging
- metadata-only audit storage without transcript persistence
- graceful fallback behavior for routing and workflow failures

## Current Technical Shape
- **API**: FastAPI
- **RAG QA path**: OpenAI + LangChain + Pinecone
- **Assessment path**: `agents/` + `assessment/` + `rules/trl_rules.json`
- **Audit store**: Firestore metadata adapter
- **Testing**: `pytest` regression coverage across QA, assessment, routing, auth, metadata, and hardening paths

## Current Delivery Status
- QA flow: implemented
- conversational assessment flow: implemented
- session-aware API contract: implemented
- Thai response templates: implemented
- release-readiness hardening: implemented

## Current Known Limitations
- no dedicated performance benchmark suite yet
- external dependency behavior is still largely mocked in automated tests
- Python runtime should be moved to `3.11+` for longer-term dependency support

## Current Release Posture
- ready for controlled pilot
- open critical defects: none identified in the current regression scope
