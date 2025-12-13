# E-Commerce Ad Creative Engine

An AI-powered workflow automation tool that generates 20 performance-ready ad creatives from a client brief using Mistral AI.

## Features

- 🎨 **Generate 40 Ad Copy Variations** - Creates diverse ad concepts with different psychological triggers
- 📊 **AI-Powered Scoring** - Selects the best 20 concepts based on performance potential
- 🖼️ **Visual Prompt Generation** - Creates detailed image generation prompts for Midjourney/DALL-E
- 🔍 **Competitor Analysis** - Analyzes market trends and competitive landscape
- 🧪 **A/B Testing Strategy** - Provides actionable testing recommendations

## Installation

```bash
npm install
```

## Setup

Set your Mistral API key as an environment variable:

```bash
export MISTRAL_API_KEY='your-api-key-here'
```

Or edit the `index.js` file to include your API key (not recommended for production).

## Usage

### Quick Start (Demo with Sample Data)

```bash
npm start
```

This will run with sample e-commerce data (Ergonomic Office Chair).

### Custom Client Brief

Edit the `sampleBrief` object in `index.js` or create your own script:

```javascript
const { generateAdCreatives } = require('./index.js');

const myClientBrief = {
  clientName: "Your Client Name",
  product: "Your Product",
  productCategory: "Product Category",
  targetAudience: "Target audience description",
  keyBenefits: "Key benefits",
  painPoints: "Customer pain points",
  usp: "Unique selling proposition",
  brandVoice: "Brand voice description",
  pricePoint: "Price point",
  brandStyle: "Brand style description",
  brandColors: "Color scheme",
  competitors: "Main competitors",
  currentWinners: "Current best performing ads (optional)"
};

generateAdCreatives(myClientBrief)
  .then(() => console.log('Complete!'))
  .catch(err => console.error('Error:', err));
```

## Output

The script generates a JSON file in `./output/{client-name}/` containing:

- 20 complete ad concepts with copy and visual prompts
- Competitor analysis report
- A/B testing strategy
- Summary statistics (formats, emotional triggers)

## Workflow Steps

1. **Generate Ad Copy** - Creates 40 variations with hooks, body copy, CTAs
2. **Score & Select** - AI evaluates and selects top 20 concepts
3. **Visual Prompts** - Generates detailed image generation prompts
4. **Competitor Analysis** - Market research and competitive insights
5. **Testing Strategy** - A/B testing recommendations

## Requirements

- Node.js >= 14.0.0
- Mistral AI API key
- Internet connection

## Next Steps After Generation

1. Review ad concepts in the generated JSON file
2. Use visual prompts with Midjourney/DALL-E to create images
3. Assemble final ads in Canva or your preferred design tool
4. Implement A/B testing strategy
5. Deliver to client

## License

MIT