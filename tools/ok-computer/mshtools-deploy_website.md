# Tool Specification: mshtools-deploy_website

## Overview
Static site deployment tool for publishing web applications to public production environments. Requires index.html as entry point.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "dist": {
      "type": "string",
      "description": "Absolute path to directory containing index.html"
    }
  },
  "required": ["dist"]
}
```

## Streaming Mechanism
- **Deployment Flow**:
  1. Validate directory exists and contains index.html
  2. Upload static assets to CDN/hosting infrastructure
  3. Configure DNS and SSL
  4. Return public URL
- **Return**: Deployment URL

## Integration Architecture

### Hosting Infrastructure
- **Provider**: Moonshot deployment service
- **CDN**: Global edge distribution
- **SSL**: Automatic HTTPS certificate provisioning
- **Domain**: Generated subdomain or custom domain support

## Requirements
- **Entry Point**: index.html must exist at root of specified directory
- **Static Only**: No server-side execution (PHP, Node.js runtime not supported)
- **Assets**: All resources must be relative paths

## Usage Patterns

### Deploy React App
```bash
# Build first
cd /mnt/okcomputer/output/app && npm run build
# Then deploy
deploy_website(dist="/mnt/okcomputer/output/app/dist")
# Returns: https://abc123.kimi.website
```

### Deploy Static HTML
```
deploy_website(dist="/mnt/kimi/output/my-site")
```

## Limitations
- **No Backend**: Cannot deploy API servers or databases
- **Static Only**: Client-side rendering only
- **Size Limits**: Total deployment size constraints apply
