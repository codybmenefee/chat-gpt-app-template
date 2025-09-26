import { z } from 'zod';
import { zodToJsonSchema } from 'zod-to-json-schema';
import * as fs from 'fs';
import * as path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

interface Tool {
  name: string;
  description: string;
  inputSchema: z.ZodSchema;
  handler: (args: any) => Promise<any>;
}

export class PDFTools {
  private tools: Tool[] = [];

  constructor() {
    this.initializeTools();
  }

  private initializeTools() {
    this.tools = [
      {
        name: 'view_pdf',
        description: 'Extract and view text content from a PDF file with comprehensive information including metadata, page count, and text preview',
        inputSchema: z.object({
          filePath: z.string().min(1, 'File path is required'),
          maxPages: z.number().min(1).max(100).default(10).optional(),
          includeMetadata: z.boolean().default(true).optional(),
          includeTextPreview: z.boolean().default(true).optional(),
        }),
        handler: this.viewPDF.bind(this),
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

  private async viewPDF(args: {
    filePath: string;
    maxPages?: number;
    includeMetadata?: boolean;
    includeTextPreview?: boolean;
  }) {
    try {
      // Check if file exists
      if (!fs.existsSync(args.filePath)) {
        throw new Error(`PDF file not found: ${args.filePath}`);
      }

      // Check if file is a PDF
      const ext = path.extname(args.filePath).toLowerCase();
      if (ext !== '.pdf') {
        throw new Error(`File is not a PDF: ${args.filePath}`);
      }

      // Get file stats
      const stats = fs.statSync(args.filePath);
      
      // Try to extract text using pdftotext (if available)
      let textContent = '';
      let pageCount = 0;
      let metadata: any = {};
      let textPreview = '';

      try {
        // Try pdftotext command
        const { stdout } = await execAsync(`pdftotext "${args.filePath}" -`);
        textContent = stdout;
        
        // Get page count
        const { stdout: pageCountOutput } = await execAsync(`pdfinfo "${args.filePath}" | grep Pages | awk '{print $2}'`);
        pageCount = parseInt(pageCountOutput.trim()) || 0;
        
        // Get text preview if requested
        if (args.includeTextPreview) {
          textPreview = textContent.substring(0, 500) + (textContent.length > 500 ? '...' : '');
        }
        
        // Get metadata if requested
        if (args.includeMetadata) {
          try {
            const { stdout: infoOutput } = await execAsync(`pdfinfo "${args.filePath}"`);
            const infoLines = infoOutput.split('\n');
            metadata = {};
            infoLines.forEach(line => {
              if (line.includes(':')) {
                const [key, value] = line.split(':', 2);
                const cleanKey = key.trim().replace(/\s+/g, '');
                metadata[cleanKey] = value.trim();
              }
            });
          } catch (metaError) {
            // Metadata extraction failed, continue without it
            console.warn('Metadata extraction failed:', metaError);
          }
        }
      } catch (cmdError) {
        // Fallback: try to read as binary and extract basic info
        textContent = `PDF file detected but text extraction failed. File size: ${this.formatFileSize(stats.size)}`;
        pageCount = 0;
        textPreview = 'Text preview not available';
        metadata = {
          note: 'Text extraction failed - pdftotext command not available or failed',
          fileSize: this.formatFileSize(stats.size),
        };
      }

      const result = {
        success: true,
        filePath: args.filePath,
        fileInfo: {
          size: stats.size,
          sizeFormatted: this.formatFileSize(stats.size),
          created: stats.birthtime,
          modified: stats.mtime,
        },
        pdfInfo: {
          pageCount: pageCount,
          ...metadata,
        },
        content: textContent,
        textPreview: args.includeTextPreview ? textPreview : undefined,
        extractedPages: Math.min(pageCount, args.maxPages || 10),
        totalPages: pageCount,
        method: 'pdftotext',
      };

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new Error(`PDF viewing failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }


  private formatFileSize(bytes: number): string {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  }
}
