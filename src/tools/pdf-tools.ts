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
        description: 'Extract and view text content from a PDF file',
        inputSchema: z.object({
          filePath: z.string().min(1, 'File path is required'),
          maxPages: z.number().min(1).max(100).default(10).optional(),
          includeMetadata: z.boolean().default(true).optional(),
        }),
        handler: this.viewPDF.bind(this),
      },
      {
        name: 'extract_pdf_text',
        description: 'Extract plain text content from a PDF file',
        inputSchema: z.object({
          filePath: z.string().min(1, 'File path is required'),
          startPage: z.number().min(1).default(1).optional(),
          endPage: z.number().min(1).default(10).optional(),
        }),
        handler: this.extractPDFText.bind(this),
      },
      {
        name: 'get_pdf_info',
        description: 'Get metadata and basic information about a PDF file',
        inputSchema: z.object({
          filePath: z.string().min(1, 'File path is required'),
        }),
        handler: this.getPDFInfo.bind(this),
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

      // Try to extract text using pdftotext (if available)
      let textContent = '';
      let pageCount = 0;
      let metadata: any = {};

      try {
        // Try pdftotext command
        const { stdout } = await execAsync(`pdftotext "${args.filePath}" -`);
        textContent = stdout;
        
        // Get page count
        const { stdout: pageCountOutput } = await execAsync(`pdfinfo "${args.filePath}" | grep Pages | awk '{print $2}'`);
        pageCount = parseInt(pageCountOutput.trim()) || 0;
        
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
        const stats = fs.statSync(args.filePath);
        textContent = `PDF file detected but text extraction failed. File size: ${this.formatFileSize(stats.size)}`;
        pageCount = 0;
        metadata = {
          note: 'Text extraction failed - pdftotext command not available or failed',
          fileSize: this.formatFileSize(stats.size),
        };
      }

      const result = {
        success: true,
        filePath: args.filePath,
        content: textContent,
        pageCount: pageCount,
        info: args.includeMetadata ? metadata : undefined,
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

  private async extractPDFText(args: {
    filePath: string;
    startPage?: number;
    endPage?: number;
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

      // Try to extract text using pdftotext
      let textContent = '';
      let pageCount = 0;

      try {
        // Try pdftotext command
        const { stdout } = await execAsync(`pdftotext "${args.filePath}" -`);
        textContent = stdout;
        
        // Get page count
        const { stdout: pageCountOutput } = await execAsync(`pdfinfo "${args.filePath}" | grep Pages | awk '{print $2}'`);
        pageCount = parseInt(pageCountOutput.trim()) || 0;
      } catch (cmdError) {
        // Fallback: basic file info
        const stats = fs.statSync(args.filePath);
        textContent = `PDF file detected but text extraction failed. File size: ${this.formatFileSize(stats.size)}`;
        pageCount = 0;
      }

      const result = {
        success: true,
        filePath: args.filePath,
        text: textContent,
        pageCount: pageCount,
        note: 'Note: Page range extraction is not directly supported. All text has been extracted.',
        requestedRange: {
          startPage: args.startPage || 1,
          endPage: args.endPage || 10,
        },
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
      throw new Error(`PDF text extraction failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  private async getPDFInfo(args: {
    filePath: string;
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
      
      let pageCount = 0;
      let pdfInfo: any = {};
      let textPreview = '';

      try {
        // Get page count
        const { stdout: pageCountOutput } = await execAsync(`pdfinfo "${args.filePath}" | grep Pages | awk '{print $2}'`);
        pageCount = parseInt(pageCountOutput.trim()) || 0;
        
        // Get PDF metadata
        const { stdout: infoOutput } = await execAsync(`pdfinfo "${args.filePath}"`);
        const infoLines = infoOutput.split('\n');
        pdfInfo = {};
        infoLines.forEach(line => {
          if (line.includes(':')) {
            const [key, value] = line.split(':', 2);
            const cleanKey = key.trim().replace(/\s+/g, '');
            pdfInfo[cleanKey] = value.trim();
          }
        });
        
        // Get text preview
        const { stdout: textOutput } = await execAsync(`pdftotext "${args.filePath}" - | head -c 500`);
        textPreview = textOutput;
      } catch (cmdError) {
        // Fallback: basic file info
        pageCount = 0;
        pdfInfo = {
          note: 'PDF info extraction failed - pdfinfo command not available or failed',
        };
        textPreview = 'Text preview not available';
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
          ...pdfInfo,
        },
        textPreview: textPreview + (textPreview.length >= 500 ? '...' : ''),
        method: 'pdfinfo',
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
      throw new Error(`PDF info extraction failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  private formatFileSize(bytes: number): string {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  }
}
