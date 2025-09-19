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

    const validatedArgs = tool.inputSchema.parse(args);
    return await tool.handler(validatedArgs);
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
