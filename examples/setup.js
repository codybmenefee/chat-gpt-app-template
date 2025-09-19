#!/usr/bin/env node

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join } from 'path';
import { createInterface } from 'readline';

const rl = createInterface({
  input: process.stdin,
  output: process.stdout,
});

function question(prompt) {
  return new Promise((resolve) => {
    rl.question(prompt, resolve);
  });
}

async function setup() {
  console.log('🚀 Wealth Portal MCP Server Setup\n');
  
  const envPath = join(process.cwd(), '.env.local');
  
  if (existsSync(envPath)) {
    const overwrite = await question('Environment file (.env.local) already exists. Overwrite? (y/N): ');
    if (overwrite.toLowerCase() !== 'y' && overwrite.toLowerCase() !== 'yes') {
      console.log('Setup cancelled.');
      rl.close();
      return;
    }
  }

  console.log('Please provide your API configuration:\n');
  console.log('Note: GraphQL endpoint is hardcoded and cannot be changed.\n');

  const apiKey = await question('API Key: ');
  const organizationId = await question('Organization ID (for theme operations): ');
  const userId = await question('User ID (for file operations): ');
  const timeout = await question('Timeout (ms) [10000]: ') || '10000';
  const retries = await question('Retries [3]: ') || '3';

  const envContent = `# GraphQL API Configuration (hardcoded endpoint)
# GRAPHQL_ENDPOINT=https://organization-gateway-service.staging.onewealth.io/graphql # Hardcoded in code
API_KEY=${apiKey}

# Optional Configuration
TIMEOUT=${timeout}
RETRIES=${retries}

# Organization and User IDs (for theme and file operations)
ORGANIZATION_ID=${organizationId}
USER_ID=${userId}
`;

  try {
    writeFileSync(envPath, envContent);
    console.log('\n✅ Configuration saved to .env.local successfully!');
    console.log('\nNext steps:');
    console.log('1. Run: npm run build');
    console.log('2. Run: npm start');
    console.log('\nOr for development:');
    console.log('1. Run: npm run dev');
  } catch (error) {
    console.error('❌ Failed to save configuration:', error.message);
  }

  rl.close();
}

setup().catch(console.error);
