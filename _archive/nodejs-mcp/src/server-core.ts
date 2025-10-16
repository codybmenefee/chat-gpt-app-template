import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import {
  CallToolRequestSchema,
  InitializeRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { GraphQLClient } from 'graphql-request';
import { z } from 'zod';
import { ConfigManager } from './config/config-manager.js';
import { GraphQLTools } from './tools/graphql-tools.js';
import { PDFTools } from './tools/pdf-tools.js';
import { ImageUploadTools } from './tools/image-upload-tools.js';
import { ConfigTools } from './tools/config-tools.js';

interface ToolHandlers {
  graphqlTools: GraphQLTools;
  pdfTools: PDFTools;
  imageUploadTools: ImageUploadTools;
  configTools: ConfigTools;
}

const ConfigSchema = z.object({
  graphqlEndpoint: z.string().url('GraphQL endpoint must be a valid URL'),
  apiKey: z.string().min(1, 'API key is required (include "Bearer " prefix if needed)'),
  timeout: z.number().min(1000).max(30000).default(10000),
  retries: z.number().min(0).max(5).default(3),
  organizationId: z.string().optional(),
  userId: z.string().optional(),
});

type Config = z.infer<typeof ConfigSchema>;

function createToolHandlers(config: Config, configManager: ConfigManager): ToolHandlers {
  const graphqlClient = new GraphQLClient(config.graphqlEndpoint, {
    headers: {
      'Authorization-API': config.apiKey,
      'Content-Type': 'application/json',
    },
  });

  const graphqlTools = new GraphQLTools(graphqlClient, configManager);
  const pdfTools = new PDFTools();
  const imageUploadTools = new ImageUploadTools(graphqlClient, configManager);
  const configTools = new ConfigTools(configManager);

  return { graphqlTools, pdfTools, imageUploadTools, configTools };
}

function registerHandlers(server: Server, handlers: ToolHandlers) {
  server.setRequestHandler(InitializeRequestSchema, async () => {
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

  server.setRequestHandler(ListToolsRequestSchema, async () => {
    console.error('ListToolsRequest received');
    try {
      const tools = [
        ...handlers.graphqlTools.getTools(),
        ...handlers.pdfTools.getTools(),
        ...handlers.imageUploadTools.getTools(),
        ...handlers.configTools.getTools(),
      ];
      console.error(`Returning ${tools.length} tools`);
      console.error('Tool names:', tools.map(t => t.name).join(', '));
      return { tools };
    } catch (error) {
      console.error('Error in ListToolsRequest:', error);
      throw error;
    }
  });

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    console.error('DEBUG MCP: Tool name:', name);
    console.error('DEBUG MCP: Raw args received:', JSON.stringify(args, null, 2));

    try {
      if (handlers.graphqlTools.hasTool(name)) {
        return await handlers.graphqlTools.handleTool(name, args);
      }

      if (handlers.pdfTools.hasTool(name)) {
        return await handlers.pdfTools.handleTool(name, args);
      }

      if (handlers.imageUploadTools.hasTool(name)) {
        return await handlers.imageUploadTools.handleTool(name, args);
      }

      if (handlers.configTools.hasTool(name)) {
        return await handlers.configTools.handleTool(name, args);
      }

      throw new Error(`Unknown tool: ${name}`);
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Error executing tool ${name}: ${
              error instanceof Error ? error.message : String(error)
            }`,
          },
        ],
        isError: true,
      };
    }
  });
}

export function createWealthPortalServer(): Server {
  const configManager = new ConfigManager();
  const config = ConfigSchema.parse(configManager.getConfig());

  const server = new Server(
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

  const handlers = createToolHandlers(config, configManager);
  registerHandlers(server, handlers);

  return server;
}

