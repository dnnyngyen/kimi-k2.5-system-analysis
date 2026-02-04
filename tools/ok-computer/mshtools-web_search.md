# Tool Specification: mshtools-web_search

## Overview
General-purpose web search capability providing real-time information retrieval from internet sources. Returns top results with relevant snippets for open-ended information retrieval.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "queries": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Array of search queries (max 5). Executed in parallel within one step.",
      "maxItems": 5
    }
  },
  "required": ["queries"]
}
```

## Streaming Mechanism
- **Transport**: Synchronous HTTP API call
- **Response Format**: Structured JSON with ranked results
- **Content**: Each result includes title, URL, snippet, and citation number
- **Citation Format**: Results tagged with [^N^] format for academic referencing
- **Parallel Execution**: Multiple queries execute simultaneously within single tool call

## Integration Architecture

### Internal Flow
1. **Query Construction**: Model formulates 1-6 word queries per guidelines
2. **API Dispatch**: Request routed to Moonshot search infrastructure
3. **Result Aggregation**: Search engine returns top-N results with metadata
4. **Context Injection**: Results streamed back to model context window
5. **Citation Binding**: Each result assigned numeric citation ID

### External Dependencies
- **Search Provider**: Integrated with general web search index
- **Rate Limiting**: Subject to per-step budget (counts as 1 of 10 steps in Base Chat, 1 of 200-300 in OK Computer)
- **Network Access**: Requires outbound HTTPS to search endpoints

## Operational Guidelines

### Query Construction
- **Optimal Length**: 1-6 words per query
- **Strategy**: Start broad, narrow if needed
- **Date Filtering**: Use `before:` and `after:` operators for temporal constraints
- **Domain Restrictions**: Use `site:` operator to limit to specific domains
- **Exclusions**: Use `-` operator to exclude terms
- **Phrase Matching**: Use `"exact phrase"` for literal matching

### Use Cases
- Frequently updated data (news, events, weather, prices)
- Unfamiliar entities recognition (people, companies, products)
- Fact-checking and verification requests
- High-impact topics requiring current information (health, finance, legal)

### Limitations
- **Result Volume**: Returns only top-N results (not comprehensive)
- **Freshness**: Index may lag real-time by minutes to hours
- **Paywall Content**: May return snippets from restricted content

## System Integration
- **Base Chat**: Available with 10-step budget per turn
- **OK Computer**: Available with extended 200-300 step budget per session
- **Citation System**: Integrates with automatic citation rendering using [^N^] format
