# Skadi - Next Steps & Future Work

## Current Status ✅

**Working Features:**
- ✅ Circuit generation from natural language
- ✅ Circuit manipulation (optimize, understand, rewrite, compare)
- ✅ CLI interface with `skadi` command
- ✅ Context7 knowledge integration (MCP-based)
- ✅ Python API for programmatic use
- ✅ 78 passing tests
- ✅ All core examples working

**Knowledge Sources:**
- ✅ Context7 (MCP-based) - Currently active and working
- ⚠️ PennyLane KB (Agno/LanceDB) - Not yet built (optional)

## Next Priority: Knowledge Base Enhancement

### Current Limitation
We're currently using Context7 only for knowledge augmentation. While this works well, adding the PennyLane Knowledge Base would provide:
- Offline capability
- Custom documentation coverage
- Hybrid knowledge retrieval (conceptual + API)

### Blocker: Embedding Model
The current implementation uses OpenAI embeddings, which requires an additional API key.

**We don't want to use OpenAI embeddings.** Instead, we need to explore:

#### Option 1: OpenRouter Embeddings
- Check if OpenRouter supports embedding models
- Would allow single API key for everything
- **Action:** Research OpenRouter embedding capabilities

#### Option 2: Open Source Embeddings (Recommended)
- **Sentence Transformers** (most popular)
  - Models: `all-MiniLM-L6-v2`, `all-mpnet-base-v2`
  - Runs locally, no API key needed
  - Very fast and lightweight
  - Reference: https://www.sbert.net/

- **Alternatives:**
  - `intfloat/e5-base-v2` (good quality)
  - `BAAI/bge-small-en-v1.5` (fast)
  - `voyage-lite-02-instruct` (if we want hosted)

#### Option 3: Hybrid Approach
- Keep Context7 for API documentation
- Add local embeddings for scraped docs
- Best of both worlds

### Implementation Tasks

**Phase 1: Research & Decide (Next)**
- [ ] Check if OpenRouter has embedding models
- [ ] Test Sentence Transformers integration with Agno/LanceDB
- [ ] Compare embedding quality for quantum computing terms
- [ ] Choose the best embedding solution

**Phase 2: Setup Playwright**
- [ ] Install Playwright: `playwright install`
- [ ] Test scrape_docs.py
- [ ] Verify scraped documentation quality
- [ ] Document scraping process

**Phase 3: Build Knowledge Base**
- [ ] Integrate chosen embedding model with PennyLaneKnowledge
- [ ] Scrape PennyLane documentation
- [ ] Load scraped docs into LanceDB
- [ ] Test hybrid knowledge retrieval (Context7 + PennyLane KB)
- [ ] Update tests to work with new embedding solution

**Phase 4: Update Examples**
- [ ] Remove OPENAI_API_KEY requirement from use_knowledge_base.py
- [ ] Make scrape_docs.py work without additional setup
- [ ] Update enhanced_generation_demo.py to showcase both sources

**Phase 5: Documentation**
- [ ] Update README with knowledge base setup instructions
- [ ] Document embedding model choice and rationale
- [ ] Add troubleshooting for knowledge base issues

## Related Examples to Reference

When implementing the knowledge base:
- `examples/use_knowledge_base.py` - Shows KB usage patterns
- `examples/scrape_docs.py` - Documentation scraping
- `examples/enhanced_generation_demo.py` - Dual knowledge system demo
- `tests/test_knowledge_protocol.py` - Knowledge system tests

## Technical Notes

**Current Knowledge Architecture:**
```python
# File: skadi/engine/knowledge_base.py
class PennyLaneKnowledge:
    def __init__(self, db_uri, embedder=None):
        # Currently hardcoded to OpenAI embeddings
        # Need to make this configurable
        pass
```

**Proposed Change:**
```python
# Support multiple embedding backends
class PennyLaneKnowledge:
    def __init__(self, db_uri, embedding_provider="sentence-transformers"):
        if embedding_provider == "sentence-transformers":
            # Use local model
        elif embedding_provider == "openrouter":
            # Use OpenRouter if available
        elif embedding_provider == "openai":
            # Legacy support
```

## Resources

**Sentence Transformers:**
- Docs: https://www.sbert.net/
- Models: https://huggingface.co/sentence-transformers
- Agno Integration: Check if Agno supports it natively

**LanceDB:**
- Embedding docs: https://lancedb.github.io/lancedb/embeddings/
- Custom embedders: https://lancedb.github.io/lancedb/embeddings/custom_embedding_function/

**OpenRouter:**
- API docs: https://openrouter.ai/docs
- Check for embedding endpoint support

## Timeline

**Immediate:** Mark optional examples and document next steps (DONE)
**Next Session:** Research embedding alternatives
**After Research:** Implement chosen solution and build knowledge base

---

*Last updated: 2024-11-16*
*Status: Research Phase - Choosing embedding solution*
