#!/usr/bin/env node

/**
 * E-COMMERCE AD CREATIVE ENGINE
 * Main workflow automation using Mistral AI
 * 
 * This script generates 20 performance-ready ad creatives from a client brief
 */

const { Mistral } = require('@mistralai/mistralai');
const fs = require('fs');
const path = require('path');

// Configuration
const MISTRAL_API_KEY = process.env.MISTRAL_API_KEY || 'YOUR_API_KEY_HERE';
const client = new Mistral({ apiKey: MISTRAL_API_KEY });

// Models to use
const MODELS = {
  large: 'mistral-large-latest',  // For complex creative tasks
  small: 'mistral-small-latest'   // For categorization and analysis
};

/**
 * STEP 1: Generate Ad Copy Variations
 * Creates 40 different ad copy concepts (we'll select best 20)
 */
async function generateAdCopy(briefData) {
  console.log('🎨 Step 1: Generating ad copy variations...');
  
  const prompt = `You are an expert direct-response copywriter specializing in e-commerce ads.

CLIENT BRIEF:
- Product: ${briefData.product}
- Target Audience: ${briefData.targetAudience}
- Key Benefits: ${briefData.keyBenefits}
- Pain Points: ${briefData.painPoints}
- Unique Selling Proposition: ${briefData.usp}
- Brand Voice: ${briefData.brandVoice}
- Price Point: ${briefData.pricePoint}
- Current Best Performers: ${briefData.currentWinners || 'None provided'}

Generate 40 different ad copy variations optimized for Facebook/Instagram ads. Include a mix of:
- 15 Hook-focused (attention-grabbing first line)
- 10 Benefit-driven (lead with transformation)
- 10 Problem-agitate-solve format
- 5 Social proof/testimonial style

For each variation provide:
1. Hook (first line - must stop the scroll)
2. Body (2-3 sentences maximum)
3. Call-to-action
4. Suggested format (static image, video, carousel)
5. Emotional trigger (curiosity, fear, desire, etc.)

Format as JSON array with this structure:
[
  {
    "hook": "...",
    "body": "...",
    "cta": "...",
    "format": "static|video|carousel",
    "emotion": "...",
    "concept": "brief description"
  }
]

Make them diverse - different angles, tones, and psychological triggers.`;

  const response = await client.chat.complete({
    model: MODELS.large,
    messages: [{ role: 'user', content: prompt }],
    temperature: 0.9,  // High creativity
    maxTokens: 4000
  });

  const content = response.choices[0].message.content;
  
  // Extract JSON from response (handle markdown code blocks)
  let jsonStr = content;
  if (content.includes('```json')) {
    jsonStr = content.split('```json')[1].split('```')[0];
  } else if (content.includes('```')) {
    jsonStr = content.split('```')[1].split('```')[0];
  }
  
  const adCopyVariations = JSON.parse(jsonStr.trim());
  
  console.log(`✅ Generated ${adCopyVariations.length} ad copy variations`);
  return adCopyVariations;
}

/**
 * STEP 2: Score and Select Best Concepts
 * Use Mistral to rate and select top 20 variations
 */
async function selectBestConcepts(adCopyVariations, briefData) {
  console.log('📊 Step 2: Scoring and selecting best 20 concepts...');
  
  const prompt = `You are a performance marketing analyst. Review these ${adCopyVariations.length} ad concepts and score each 1-10 based on:
- Attention-grabbing potential (stops the scroll)
- Relevance to target audience: ${briefData.targetAudience}
- Clarity of value proposition
- Call-to-action strength
- Likelihood to convert

Return JSON array with scores and select top 20:
{
  "scored": [{"index": 0, "score": 8.5, "reasoning": "..."}],
  "top20": [0, 3, 5, ...]  // Array of indices
}

Ad concepts to evaluate:
${JSON.stringify(adCopyVariations, null, 2)}`;

  const response = await client.chat.complete({
    model: MODELS.large,
    messages: [{ role: 'user', content: prompt }],
    temperature: 0.3,  // More deterministic for scoring
    maxTokens: 3000
  });

  const content = response.choices[0].message.content;
  let jsonStr = content;
  if (content.includes('```json')) {
    jsonStr = content.split('```json')[1].split('```')[0];
  } else if (content.includes('```')) {
    jsonStr = content.split('```')[1].split('```')[0];
  }
  
  const scores = JSON.parse(jsonStr.trim());
  const topConcepts = scores.top20.map(idx => adCopyVariations[idx]);
  
  console.log(`✅ Selected top 20 concepts (avg score: ${(scores.scored.reduce((sum, s) => sum + s.score, 0) / scores.scored.length).toFixed(1)})`);
  return topConcepts;
}

/**
 * STEP 3: Generate Visual Descriptions for Each Ad
 * Create detailed image generation prompts
 */
async function generateVisualPrompts(adConcepts, briefData) {
  console.log('🖼️  Step 3: Generating visual descriptions...');
  
  const enhancedConcepts = [];
  
  for (let i = 0; i < adConcepts.length; i++) {
    const concept = adConcepts[i];
    
    const prompt = `Create a detailed image generation prompt for this ad concept:

Ad Copy: ${concept.hook} ${concept.body}
Product: ${briefData.product}
Brand Style: ${briefData.brandStyle || 'modern, clean, professional'}
Target Audience: ${briefData.targetAudience}

Generate a Midjourney/DALL-E prompt that will create a scroll-stopping visual for this ad.
Include:
- Main subject/focal point
- Setting/background
- Colors (align with ${briefData.brandColors || 'brand'})
- Mood/atmosphere
- Composition style (close-up, lifestyle, product focus, etc.)
- Any text overlay positions

Also suggest 2-3 alternative visual angles.

Format as JSON:
{
  "primary_prompt": "...",
  "alternatives": ["...", "...", "..."],
  "layout_suggestion": "...",
  "text_overlay_position": "top|center|bottom"
}`;

    const response = await client.chat.complete({
      model: MODELS.large,
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.8,
      maxTokens: 500
    });

    const content = response.choices[0].message.content;
    let jsonStr = content;
    if (content.includes('```json')) {
      jsonStr = content.split('```json')[1].split('```')[0];
    } else if (content.includes('```')) {
      jsonStr = content.split('```')[1].split('```')[0];
    }
    
    const visualDetails = JSON.parse(jsonStr.trim());
    
    enhancedConcepts.push({
      ...concept,
      visualPrompt: visualDetails.primary_prompt,
      alternativeVisuals: visualDetails.alternatives,
      layout: visualDetails.layout_suggestion,
      textPosition: visualDetails.text_overlay_position,
      adNumber: i + 1
    });
    
    console.log(`  ✓ Ad ${i + 1}/20 visual prompt created`);
  }
  
  console.log('✅ All visual prompts generated');
  return enhancedConcepts;
}

/**
 * STEP 4: Competitor Analysis
 * Analyze competitor ads and market trends
 */
async function generateCompetitorAnalysis(briefData) {
  console.log('🔍 Step 4: Running competitor analysis...');
  
  const prompt = `You are a competitive intelligence analyst for e-commerce.

Analyze the competitive landscape for:
- Product Category: ${briefData.productCategory}
- Target Market: ${briefData.targetAudience}
- Competitors: ${briefData.competitors || 'Top 3 in category'}

Provide analysis on:
1. Common ad formats being used
2. Messaging patterns and hooks
3. Visual styles trending in this category
4. Pricing/promotion strategies
5. Gaps/opportunities for differentiation

Also provide 5 specific recommendations for our client's ad strategy.

Format as structured markdown report.`;

  const response = await client.chat.complete({
    model: MODELS.large,
    messages: [{ role: 'user', content: prompt }],
    temperature: 0.5,
    maxTokens: 2000
  });

  console.log('✅ Competitor analysis complete');
  return response.choices[0].message.content;
}

/**
 * STEP 5: A/B Testing Recommendations
 * Generate testing strategy for the ad concepts
 */
async function generateTestingStrategy(adConcepts) {
  console.log('🧪 Step 5: Creating A/B testing recommendations...');
  
  const prompt = `You are a performance marketing scientist.

Given these ${adConcepts.length} ad concepts, create an A/B testing strategy:

${adConcepts.map((ad, i) => `Ad ${i+1}: ${ad.hook} (${ad.format}, ${ad.emotion})`).join('\n')}

Recommend:
1. Which ads to test head-to-head (create 5 test groups)
2. What variables to test (copy vs image vs format)
3. Success metrics to track
4. Budget allocation strategy
5. How to identify winners quickly

Format as actionable markdown guide.`;

  const response = await client.chat.complete({
    model: MODELS.large,
    messages: [{ role: 'user', content: prompt }],
    temperature: 0.4,
    maxTokens: 1500
  });

  console.log('✅ Testing strategy created');
  return response.choices[0].message.content;
}

/**
 * MAIN WORKFLOW
 */
async function generateAdCreatives(clientBrief) {
  console.log('🚀 Starting E-Commerce Ad Creative Engine\n');
  console.log(`Client: ${clientBrief.clientName}`);
  console.log(`Product: ${clientBrief.product}\n`);
  
  try {
    // Step 1: Generate 40 copy variations
    const allCopyVariations = await generateAdCopy(clientBrief);
    
    // Step 2: Select best 20
    const topConcepts = await selectBestConcepts(allCopyVariations, clientBrief);
    
    // Step 3: Add visual prompts
    const finalAdConcepts = await generateVisualPrompts(topConcepts, clientBrief);
    
    // Step 4: Competitor analysis
    const competitorAnalysis = await generateCompetitorAnalysis(clientBrief);
    
    // Step 5: Testing strategy
    const testingStrategy = await generateTestingStrategy(finalAdConcepts);
    
    // Compile final deliverable package
    const deliverablePackage = {
      client: clientBrief.clientName,
      generatedDate: new Date().toISOString().split('T')[0],
      adCreatives: finalAdConcepts,
      competitorAnalysis: competitorAnalysis,
      testingStrategy: testingStrategy,
      summary: {
        totalAds: finalAdConcepts.length,
        formats: {
          static: finalAdConcepts.filter(a => a.format === 'static').length,
          video: finalAdConcepts.filter(a => a.format === 'video').length,
          carousel: finalAdConcepts.filter(a => a.format === 'carousel').length
        },
        emotions: finalAdConcepts.reduce((acc, ad) => {
          acc[ad.emotion] = (acc[ad.emotion] || 0) + 1;
          return acc;
        }, {})
      }
    };
    
    // Save to file
    const outputDir = path.join(__dirname, 'output', clientBrief.clientName.replace(/\s+/g, '-'));
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    const outputFile = path.join(outputDir, `ad-creatives-${new Date().toISOString().split('T')[0]}.json`);
    fs.writeFileSync(outputFile, JSON.stringify(deliverablePackage, null, 2));
    
    console.log('\n✅ COMPLETE! Ad creative package generated');
    console.log(`📁 Output saved to: ${outputFile}`);
    console.log('\nNext Steps:');
    console.log('1. Review ad concepts in JSON file');
    console.log('2. Use visual prompts with Midjourney/DALL-E');
    console.log('3. Assemble final ads in Canva');
    console.log('4. Deliver to client via Google Drive\n');
    
    return deliverablePackage;
    
  } catch (error) {
    console.error('❌ Error generating ad creatives:', error.message);
    throw error;
  }
}

// Example usage
if (require.main === module) {
  // Sample client brief
  const sampleBrief = {
    clientName: "Sample E-Commerce Store",
    product: "Ergonomic Office Chair",
    productCategory: "Home Office Furniture",
    targetAudience: "Remote workers, 25-45, desk job professionals, health-conscious",
    keyBenefits: "Reduces back pain, improves posture, increases productivity, premium materials",
    painPoints: "Back pain from long sitting, poor posture, uncomfortable cheap chairs, lack of lumbar support",
    usp: "Doctor-designed ergonomic support with 30-day pain-free guarantee",
    brandVoice: "Professional, helpful, health-focused, trustworthy",
    pricePoint: "$399 (premium mid-range)",
    brandStyle: "Clean, modern, minimalist with blue/white color scheme",
    brandColors: "Navy blue (#1F4788), white, light gray accents",
    competitors: "Herman Miller, Steelcase, Autonomous",
    currentWinners: "Ads focusing on 'work from home back pain' perform best"
  };
  
  console.log('⚠️  This is a demo with sample data.');
  console.log('📝 Edit the sampleBrief object above or pass real client data.\n');
  
  generateAdCreatives(sampleBrief)
    .then(() => console.log('Done!'))
    .catch(err => console.error('Failed:', err));
}

module.exports = { generateAdCreatives };
