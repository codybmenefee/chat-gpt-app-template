#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  InitializeRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { GraphQLClient } from 'graphql-request';
import { z } from 'zod';
import { GraphQLTools } from './tools/graphql-tools.js';
import { PDFTools } from './tools/pdf-tools.js';
import { ImageUploadTools } from './tools/image-upload-tools.js';
import { ConfigTools } from './tools/config-tools.js';
import { ConfigManager } from './config/config-manager.js';

// Configuration schema
const ConfigSchema = z.object({
  graphqlEndpoint: z.string().url('GraphQL endpoint must be a valid URL'),
  apiKey: z.string().min(1, 'API key is required (include "Bearer " prefix if needed)'),
  timeout: z.number().min(1000).max(30000).default(10000),
  retries: z.number().min(0).max(5).default(3),
  organizationId: z.string().optional(),
  userId: z.string().optional(),
});

type Config = z.infer<typeof ConfigSchema>;

class WealthPortalMCPServer {
  private server: Server;
  private graphqlClient: GraphQLClient;
  private config: Config;
  private configManager: ConfigManager;
  private graphqlTools: GraphQLTools;
  private pdfTools: PDFTools;
  private imageUploadTools: ImageUploadTools;
  private configTools: ConfigTools;

  constructor() {
    this.server = new Server(
      {
        name: 'wealth-portal-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {
            listChanged: true,
          },
        },
      }
    );

    this.configManager = new ConfigManager();
    this.config = this.configManager.getConfig();
    this.graphqlClient = new GraphQLClient(this.config.graphqlEndpoint, {
      headers: {
        'Authorization-API': this.config.apiKey,
        'Content-Type': 'application/json',
      },
    });

    this.graphqlTools = new GraphQLTools(this.graphqlClient, this.configManager);
    this.pdfTools = new PDFTools();
    this.imageUploadTools = new ImageUploadTools(this.graphqlClient, this.configManager);
    this.configTools = new ConfigTools(this.configManager);

    this.setupHandlers();
  }


  private setupHandlers() {
    // Handle initialization request
    this.server.setRequestHandler(InitializeRequestSchema, async () => {
      console.error('InitializeRequest received');
      return {
        protocolVersion: '2024-11-05',
        capabilities: {
          tools: {
            listChanged: true,
          },
        },
        serverInfo: {
          name: 'wealth-portal-mcp-server',
          version: '1.0.0',
        },
      };
    });

    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      console.error('ListToolsRequest received');
      const tools = [
        ...this.graphqlTools.getTools(),
        ...this.pdfTools.getTools(),
        ...this.imageUploadTools.getTools(),
        ...this.configTools.getTools(),
      ];
      console.error(`Returning ${tools.length} tools`);
      return { tools };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      
      console.error('DEBUG MCP: Tool name:', name);
      console.error('DEBUG MCP: Raw args received:', JSON.stringify(args, null, 2));

      try {
        // Route to appropriate tool handler
        if (this.graphqlTools.hasTool(name)) {
          return await this.graphqlTools.handleTool(name, args);
        }
        
        if (this.pdfTools.hasTool(name)) {
          return await this.pdfTools.handleTool(name, args);
        }
        
        if (this.imageUploadTools.hasTool(name)) {
          return await this.imageUploadTools.handleTool(name, args);
        }
        
        if (this.configTools.hasTool(name)) {
          return await this.configTools.handleTool(name, args);
        }

        throw new Error(`Unknown tool: ${name}`);
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error executing tool ${name}: ${error instanceof Error ? error.message : String(error)}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  async run() {
    try {
      const transport = new StdioServerTransport();
      await this.server.connect(transport);
      console.error('Wealth Portal MCP Server running on stdio');
      
      // Keep the process alive
      process.stdin.resume();
    } catch (error) {
      console.error('Failed to start MCP server:', error);
      process.exit(1);
    }
  }
}

// Start the server
const server = new WealthPortalMCPServer();
server.run().catch((error) => {
  console.error('Failed to start server:', error);
  process.exit(1);
});