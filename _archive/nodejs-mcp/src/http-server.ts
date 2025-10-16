import { createServer as createHttpServer, ServerResponse } from 'http';
import { AddressInfo } from 'net';
import { URL } from 'url';
import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';

interface HttpServerOptions {
  port: number;
  corsOrigin?: string;
}

interface SessionInfo {
  transport: SSEServerTransport;
  server: Server;
}

export class MCPHttpServer {
  private app = express();
  private server = createHttpServer(this.app);
  private sessions = new Map<string, SessionInfo>();

  constructor(private readonly serverFactory: () => Server, private readonly options: HttpServerOptions) {
    this.configureMiddleware();
    this.configureRoutes();
  }

  private configureMiddleware() {
    this.app.use(cors({ origin: this.options.corsOrigin ?? true }));

    this.app.use((req: Request, _res: Response, next: NextFunction) => {
      console.error(`[HTTP] ${req.method} ${req.url}`);
      next();
    });
  }

  private configureRoutes() {
    this.app.get('/health', (_req, res) => {
      res.json({ status: 'ok' });
    });

    this.app.get('/mcp', async (req, res) => {
      try {
        const baseUrl = new URL(req.protocol + '://' + req.get('host') + req.originalUrl);
        baseUrl.search = '';
        const endpoint = `${baseUrl.toString().replace(/\/$/, '')}`;

        const transport = new SSEServerTransport(endpoint, res as unknown as ServerResponse);
        const server = this.serverFactory();

        await server.connect(transport);
        // Note: transport.start() is called automatically by server.connect()

        const sessionId = transport.sessionId;
        this.sessions.set(sessionId, { transport, server });

        res.on('close', async () => {
          console.error(`[HTTP] SSE connection closed (${sessionId})`);
          this.sessions.delete(sessionId);
          await Promise.allSettled([
            transport.close(),
            server.close(),
          ]).then((results) => {
            results.forEach((result) => {
              if (result.status === 'rejected') {
                console.error('[HTTP] Error during session cleanup:', result.reason);
              }
            });
          });
        });

        // Keep the connection alive by sending periodic heartbeats
        const heartbeat = setInterval(() => {
          if (res.headersSent) {
            try {
              res.write(': heartbeat\n\n');
            } catch (error) {
              console.error('[HTTP] Error sending heartbeat:', error);
              clearInterval(heartbeat);
            }
          } else {
            clearInterval(heartbeat);
          }
        }, 30000); // Send heartbeat every 30 seconds

        res.on('close', () => {
          clearInterval(heartbeat);
        });

        console.error(`[HTTP] SSE session established (${sessionId})`);
        console.error(`[HTTP] Active sessions: ${this.sessions.size}`);
      } catch (error) {
        console.error('[HTTP] Failed to start SSE session', error);
        if (!res.headersSent) {
          res.status(500).json({ error: 'Failed to establish SSE connection' });
        }
      }
    });

    this.app.post('/mcp', express.json({ limit: '4mb' }), async (req, res) => {
      const sessionId = typeof req.query.sessionId === 'string' ? req.query.sessionId : undefined;
      if (!sessionId) {
        res.status(400).json({ error: 'Missing sessionId query parameter' });
        return;
      }

      const session = this.sessions.get(sessionId);
      console.error(`[HTTP] Looking for session ${sessionId}, found: ${!!session}`);
      console.error(`[HTTP] Available sessions: ${Array.from(this.sessions.keys()).join(', ')}`);
      if (!session) {
        res.status(404).json({ error: 'Session not found or expired' });
        return;
      }

      try {
        // Handle the message directly instead of using handlePostMessage
        const message = req.body;
        await session.transport.handleMessage(message);
        res.status(202).json({ status: 'accepted' });
      } catch (error) {
        console.error('[HTTP] Error handling POST message', error);
        if (!res.headersSent) {
          res.status(500).json({ error: 'Failed to process message' });
        }
      }
    });

    this.app.use((err: unknown, _req: Request, res: Response, _next: NextFunction) => {
      console.error('[HTTP] Unhandled error', err);
      res.status(500).json({ error: 'Internal server error' });
    });
  }

  async start(): Promise<number> {
    return new Promise((resolve, reject) => {
      this.server.once('error', reject);
      this.server.listen(this.options.port, () => {
        const address = this.server.address() as AddressInfo;
        console.error(`[HTTP] MCP server listening on port ${address.port}`);
        resolve(address.port);
      });
    });
  }

  async stop(): Promise<void> {
    for (const [sessionId, session] of this.sessions.entries()) {
      await Promise.allSettled([
        session.transport.close(),
        session.server.close(),
      ]).then((results) => {
        results.forEach((result) => {
          if (result.status === 'rejected') {
            console.error(`[HTTP] Error closing session ${sessionId}:`, result.reason);
          }
        });
      });
      this.sessions.delete(sessionId);
    }

    return new Promise((resolve, reject) => {
      this.server.close((error) => {
        if (error) {
          reject(error);
        } else {
          resolve();
        }
      });
    });
  }
}

