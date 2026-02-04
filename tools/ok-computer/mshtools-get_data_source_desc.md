# Tool Specification: mshtools-get_data_source_desc

## Overview
Metadata retrieval for structured data sources. Returns available APIs, parameters, and usage details for financial, economic, and academic databases.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "data_source_name": {
      "type": "string",
      "enum": ["yahoo_finance", "world_bank_open_data", "arxiv", "google_scholar"],
      "description": "Name of the data source to describe"
    }
  },
  "required": ["data_source_name"]
}
```

## Streaming Mechanism
- **Response Format**: Structured documentation of available APIs
- **Content Includes**:
  - Available API endpoints
  - Required vs optional parameters
  - Return value descriptions
  - Usage examples

## Supported Data Sources

### yahoo_finance
Financial stock data including prices, company info, financial statements, analyst coverage.

### world_bank_open_data
Global development indicators (GDP, population, poverty, education, health).

### arxiv
Scientific preprints search, download, conversion to markdown.

### google_scholar
Academic literature search, citations, author profiles.

## Usage Pattern

### Discovery Flow
```
get_data_source_desc(data_source_name="yahoo_finance")
# Returns API documentation

get_data_source(
  data_source_name="yahoo_finance",
  api_name="get_historical_stock_prices",
  params={"ticker": "AAPL", "period": "1y"}
)
```

## Related Tools
- `get_data_source`: Execute actual data query after reading description
