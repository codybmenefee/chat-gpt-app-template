#!/usr/bin/env node

import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { createWealthPortalServer } from './server-core.js';
import { MCPHttpServer } from './http-server.js';

const DEFAULT_PORT = 3000;

async function start() {
  const transportMode = (process.env.TRANSPORT ?? 'stdio').toLowerCase();
  if (transportMode === 'http') {
    const port = process.env.HTTP_PORT ? Number(process.env.HTTP_PORT) : DEFAULT_PORT;
    if (Number.isNaN(port) || port <= 0) {
      throw new Error(`Invalid HTTP_PORT value: ${process.env.HTTP_PORT}`);
    }

    const corsOrigin = process.env.HTTP_CORS_ORIGIN;
    const httpServer = new MCPHttpServer(createWealthPortalServer, {
      port,
      ...(corsOrigin ? { corsOrigin } : {}),
    });

    await httpServer.start();
    console.error(`Wealth Portal MCP Server running over HTTP on port ${port}`);
    return;
  }

  if (transportMode !== 'stdio') {
    throw new Error(`Unsupported TRANSPORT mode: ${transportMode}`);
  }

  const server = createWealthPortalServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Wealth Portal MCP Server running on stdio');
  process.stdin.resume();
}

start().catch((error) => {
  console.error('Failed to start server:', error);
  process.exit(1);
});