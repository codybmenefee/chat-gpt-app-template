import { GraphQLClient } from 'graphql-request';
import { z } from 'zod';
import { zodToJsonSchema } from 'zod-to-json-schema';
import { ConfigManager } from '../config/config-manager.js';

interface Tool {
  name: string;
  description: string;
  inputSchema: z.ZodSchema;
  handler: (args: any) => Promise<any>;
}

export class GraphQLTools {
  private tools: Tool[] = [];
  private configManager: ConfigManager;

  constructor(_client: GraphQLClient, configManager: ConfigManager) {
    this.configManager = configManager;
    this.initializeTools();
  }

  private initializeTools() {
    // TEMPORARILY DISABLED FOR CHATGPT CONNECTION TESTING
    // All complex tools commented out to test minimal connection
    this.tools = [];
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

    // Validate configuration
    if (!this.configManager.isConfigured()) {
      throw new Error('Server configuration is incomplete. Use config_set to configure API key and other required settings.');
    }

      const validatedArgs = tool.inputSchema.parse(args);
      return await tool.handler(validatedArgs);
  }
}