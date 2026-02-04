# Tool Specification: get_data_source_desc (Base Chat)

## Overview
Data source metadata retrieval for Base Chat.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "data_source_name": {
      "type": "string",
      "enum": ["yahoo_finance", "world_bank_open_data", "arxiv", "google_scholar"]
    }
  },
  "required": ["data_source_name"]
}
```

## Usage
```
get_data_source_desc(data_source_name="yahoo_finance")
```

## Note
Identical to OK Computer mshtools-get_data_source_desc.
