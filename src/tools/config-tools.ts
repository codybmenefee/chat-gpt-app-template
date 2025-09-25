import { z } from 'zod';
import { zodToJsonSchema } from 'zod-to-json-schema';
import { ConfigManager, Config } from '../config/config-manager.js';

interface Tool {
  name: string;
  description: string;
  inputSchema: z.ZodSchema;
  handler: (args: any) => Promise<any>;
}

export class ConfigTools {
  private configManager: ConfigManager;
  private tools: Tool[] = [];
  private failedAttempts: Map<string, { count: number; lastAttempt: number; errors: string[] }> = new Map();

  constructor(configManager: ConfigManager) {
    this.configManager = configManager;
    this.initializeTools();
  }

  private initializeTools() {
    this.tools = [
      {
        name: 'config_get',
        description: 'Get the current MCP server configuration',
        inputSchema: z.object({}),
        handler: this.getConfig.bind(this),
      },
      {
        name: 'config_set',
        description: 'Update the MCP server configuration',
        inputSchema: z.object({
          apiKey: z.string().optional(),
          timeout: z.number().min(1000).max(30000).optional(),
          retries: z.number().min(0).max(5).optional(),
          organizationId: z.string().optional(),
          userId: z.string().optional(),
        }),
        handler: this.setConfig.bind(this),
      },
      {
        name: 'config_reset',
        description: 'Reset the configuration to defaults',
        inputSchema: z.object({}),
        handler: this.resetConfig.bind(this),
      },
      {
        name: 'config_status',
        description: 'Check if the configuration is complete and valid',
        inputSchema: z.object({}),
        handler: this.getConfigStatus.bind(this),
      },
    ];
  }

  getTools() {
    return this.tools.map(tool => ({
      name: tool.name,
      description: tool.description,
      inputSchema: zodToJsonSchema(tool.inputSchema),
    }));
  }

  hasTool(name: string): boolean {
    return this.tools.some(tool => tool.name === name);
  }

  async handleTool(name: string, args: any) {
    const tool = this.tools.find(t => t.name === name);
    if (!tool) {
      throw new Error(`Tool ${name} not found`);
    }

    try {
      const validatedArgs = tool.inputSchema.parse(args);
      
      // Clear failed attempts on successful validation
      this.clearFailedAttempts(name);
      
      return await tool.handler(validatedArgs);
    } catch (validationError) {
      // Track failed attempts for loop detection
      this.trackFailedAttempt(name, validationError instanceof Error ? validationError.message : String(validationError));
      
      // Check if we're in a loop (3+ failed attempts in last 2 minutes)
      const attemptInfo = this.failedAttempts.get(name);
      if (attemptInfo && attemptInfo.count >= 3 && (Date.now() - attemptInfo.lastAttempt) < 120000) {
        const errorMessage = `LOOP DETECTED: This tool has failed ${attemptInfo.count} times in the last 2 minutes with similar errors. Please STOP retrying and ask the user for clarification or different parameters. Recent errors: ${attemptInfo.errors.slice(-3).join('; ')}`;
        throw new Error(errorMessage);
      }
      
      // Re-throw the original validation error
      throw validationError;
    }
  }

  private trackFailedAttempt(toolName: string, errorMessage: string) {
    const now = Date.now();
    const existing = this.failedAttempts.get(toolName);
    
    if (existing) {
      // Reset if more than 5 minutes have passed
      if (now - existing.lastAttempt > 300000) {
        this.failedAttempts.set(toolName, {
          count: 1,
          lastAttempt: now,
          errors: [errorMessage]
        });
      } else {
        // Increment count and add error
        existing.count++;
        existing.lastAttempt = now;
        existing.errors.push(errorMessage);
        // Keep only last 5 errors
        if (existing.errors.length > 5) {
          existing.errors = existing.errors.slice(-5);
        }
      }
    } else {
      this.failedAttempts.set(toolName, {
        count: 1,
        lastAttempt: now,
        errors: [errorMessage]
      });
    }
  }

  private clearFailedAttempts(toolName: string) {
    this.failedAttempts.delete(toolName);
  }

  private async getConfig() {
    const config = this.configManager.getConfig();
    
    // Don't expose sensitive information
    const safeConfig = {
      ...config,
      apiKey: config.apiKey ? '***' + config.apiKey.slice(-4) : '',
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(safeConfig, null, 2),
        },
      ],
    };
  }

  private async setConfig(args: Partial<Config>) {
    try {
      this.configManager.updateConfig(args);
      
      return {
        content: [
          {
            type: 'text',
            text: 'Configuration updated successfully',
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to update configuration: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  private async resetConfig() {
    try {
      this.configManager.resetConfig();
      
      return {
        content: [
          {
            type: 'text',
            text: 'Configuration reset to defaults',
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to reset configuration: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  private async getConfigStatus() {
    const isConfigured = this.configManager.isConfigured();
    const isFullyConfigured = this.configManager.isFullyConfigured();
    const config = this.configManager.getConfig();
    
    const status = {
      isConfigured,
      isFullyConfigured,
      hasGraphQLEndpoint: config.graphqlEndpoint !== '',
      hasApiKey: config.apiKey !== '',
      hasOrganizationId: config.organizationId !== '',
      hasUserId: config.userId !== '',
      timeout: config.timeout,
      retries: config.retries,
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(status, null, 2),
        },
      ],
    };
  }
}
