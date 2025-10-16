import { writeFileSync } from 'fs';
import { join } from 'path';
import { z } from 'zod';
import { config } from 'dotenv';

const ConfigSchema = z.object({
  graphqlEndpoint: z.string().url(),
  apiKey: z.string(),
  timeout: z.number().default(10000),
  retries: z.number().default(3),
  organizationId: z.string().optional(),
  userId: z.string().optional(),
});

// Hardcoded GraphQL endpoint since it's consistent
const HARDCODED_GRAPHQL_ENDPOINT = 'https://organization-gateway-service.staging.onewealth.io/graphql';

export type Config = z.infer<typeof ConfigSchema>;

export class ConfigManager {
  private envPath: string;
  private config: Config | null = null;

  constructor() {
    this.envPath = join(process.cwd(), '.env.local');
    // Load environment variables from .env.local
    config({ path: this.envPath });
  }

  getConfig(): Config {
    if (this.config) {
      return this.config;
    }

    // Load configuration from environment variables (.env.local only)
    const envConfig = {
      graphqlEndpoint: HARDCODED_GRAPHQL_ENDPOINT, // Hardcoded as it's consistent
      apiKey: process.env.API_KEY || '',
      timeout: process.env.TIMEOUT ? parseInt(process.env.TIMEOUT, 10) : 10000,
      retries: process.env.RETRIES ? parseInt(process.env.RETRIES, 10) : 3,
      organizationId: process.env.ORGANIZATION_ID || '',
      userId: process.env.USER_ID || '',
    };

    this.config = envConfig;
    return this.config;
  }

  updateConfig(updates: Partial<Config>): void {
    const currentConfig = this.getConfig();
    const newConfig = { ...currentConfig, ...updates };
    
    // Prevent updating the hardcoded GraphQL endpoint
    if (updates.graphqlEndpoint && updates.graphqlEndpoint !== HARDCODED_GRAPHQL_ENDPOINT) {
      throw new Error('GraphQL endpoint is hardcoded and cannot be changed');
    }
    
    try {
      ConfigSchema.parse(newConfig);
      this.config = newConfig;
      
      // Update .env.local file
      this.updateEnvFile(newConfig);
    } catch (error) {
      throw new Error(`Invalid config: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  resetConfig(): void {
    this.config = null;
    // Reset .env.local file to defaults
    const defaultConfig = {
      graphqlEndpoint: HARDCODED_GRAPHQL_ENDPOINT,
      apiKey: '',
      timeout: 10000,
      retries: 3,
      organizationId: '',
      userId: '',
    };
    this.updateEnvFile(defaultConfig);
  }

  isConfigured(): boolean {
    const config = this.getConfig();
    return config.graphqlEndpoint !== '' && config.apiKey !== '';
  }

  isFullyConfigured(): boolean {
    const config = this.getConfig();
    return config.graphqlEndpoint !== '' && 
           config.apiKey !== '' && 
           config.organizationId !== '' && 
           config.userId !== '';
  }

  getOrganizationId(): string {
    const config = this.getConfig();
    if (!config.organizationId) {
      throw new Error('Organization ID not configured. Use config_set to set organizationId.');
    }
    return config.organizationId;
  }

  getUserId(): string {
    const config = this.getConfig();
    if (!config.userId) {
      throw new Error('User ID not configured. Use config_set to set userId.');
    }
    return config.userId;
  }

  private updateEnvFile(config: Config): void {
    const envContent = `# GraphQL API Configuration (hardcoded endpoint)
# GRAPHQL_ENDPOINT=${config.graphqlEndpoint} # Hardcoded in code
API_KEY=${config.apiKey}

# Optional Configuration
TIMEOUT=${config.timeout}
RETRIES=${config.retries}

# Organization and User IDs (for theme and file operations)
ORGANIZATION_ID=${config.organizationId}
USER_ID=${config.userId}
`;

    writeFileSync(this.envPath, envContent);
  }
}
