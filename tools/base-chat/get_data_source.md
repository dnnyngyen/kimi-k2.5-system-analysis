# Tool Specification: get_data_source (Base Chat)

## Overview
Structured data retrieval for Base Chat.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "data_source_name": {
      "type": "string",
      "enum": ["yahoo_finance", "world_bank_open_data", "arxiv", "google_scholar"]
    },
    "api_name": {"type": "string"},
    "params": {"type": "object"}
  },
  "required": ["data_source_name", "api_name", "params"]
}
```

## Usage
```
get_data_source(
  data_source_name="yahoo_finance",
  api_name="get_stock_info",
  params={"ticker": "AAPL"}
)
```

## Note
Identical to OK Computer mshtools-get_data_source.
