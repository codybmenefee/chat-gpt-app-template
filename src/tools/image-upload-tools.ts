import { GraphQLClient } from 'graphql-request';
import { z } from 'zod';
import { zodToJsonSchema } from 'zod-to-json-schema';
import { readFileSync } from 'fs';
import { ConfigManager } from '../config/config-manager.js';

interface Tool {
  name: string;
  description: string;
  inputSchema: z.ZodSchema;
  handler: (args: any) => Promise<any>;
}

export class ImageUploadTools {
  private client: GraphQLClient;
  private tools: Tool[] = [];
  private configManager: ConfigManager;

  constructor(client: GraphQLClient, configManager: ConfigManager) {
    this.client = client;
    this.configManager = configManager;
    this.initializeTools();
  }

  private initializeTools() {
    this.tools = [
      {
        name: 'upload_file',
        description: 'Upload any file to S3 and create a file document record. Use for general file uploads (documents, images, etc.). For organization logos specifically, prefer update_organization_theme tool. If objectId/userId are not provided, uses configured values from .env.local.',
        // NOTE: For organization logos, use update_organization_theme instead
        inputSchema: z.object({
          filePath: z.string().min(1, 'File path is required'),
          fileName: z.string().min(1, 'File name is required').optional(),
          objectType: z.enum(['ORGANIZATION', 'USER', 'CLIENT']).default('ORGANIZATION'),
          objectId: z.string().min(1, 'Object ID is required').optional(),
          type: z.enum(['LOGO', 'AVATAR', 'DOCUMENT', 'IMAGE']).default('LOGO'),
          userId: z.string().min(1, 'User ID is required').optional(),
          permissionType: z.enum(['PUBLIC', 'PRIVATE', 'RESTRICTED']).default('PUBLIC'),
          updateTheme: z.boolean().default(false),
        }),
        handler: this.uploadFile.bind(this),
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

    // Validate configuration
    if (!this.configManager.isConfigured()) {
      throw new Error('Server configuration is incomplete. Use config_set to configure API key and other required settings.');
    }

    // Pre-validate for placeholder values before parsing
    if (args.objectId && (args.objectId.includes('your_') || args.objectId.includes('placeholder') || args.objectId.includes('_here'))) {
      throw new Error('Invalid organization ID provided. Please omit the objectId parameter to use the configured value, or provide a valid organization ID.');
    }
    if (args.userId && (args.userId.includes('your_') || args.userId.includes('placeholder') || args.userId.includes('_here'))) {
      throw new Error('Invalid user ID provided. Please omit the userId parameter to use the configured value, or provide a valid user ID.');
    }

    const validatedArgs = tool.inputSchema.parse(args);
    return await tool.handler(validatedArgs);
  }

  private async uploadFile(args: {
    filePath: string;
    fileName?: string;
    objectType: 'ORGANIZATION' | 'USER' | 'CLIENT';
    objectId?: string;
    type: 'LOGO' | 'AVATAR' | 'DOCUMENT' | 'IMAGE';
    userId?: string;
    permissionType: 'PUBLIC' | 'PRIVATE' | 'RESTRICTED';
    updateTheme: boolean;
  }) {
    try {
      const objectId = args.objectId || this.configManager.getOrganizationId();
      const userId = args.userId || this.configManager.getUserId();
      const fileName = args.fileName || args.filePath.split('/').pop() || 'uploaded-file';


      if (!objectId) {
        throw new Error('Organization ID is required. Set ORGANIZATION_ID environment variable or provide objectId parameter.');
      }
      if (!userId) {
        throw new Error('User ID is required. Set USER_ID environment variable or provide userId parameter.');
      }

      console.log(`🚀 Starting file upload: ${fileName}`);

      // Step 1: Get upload URL
      console.log('📡 Getting upload URL...');
      const uploadUrlQuery = `
        query fetchFileUploadUrl($input: FetchFileUploadUrlInput!) {
          fetchFileUploadUrl(input: $input) {
            temporarySignedURL
            timestamp
            __typename
          }
        }
      `;

      const uploadUrlVariables = {
        input: {
          objectType: args.objectType,
          objectId: objectId,
          fileName: fileName,
          type: args.type,
          userId: userId,
          generateUniqueFileName: true,
        },
      };

      const uploadUrlResult = await this.client.request(uploadUrlQuery, uploadUrlVariables) as any;
      const { temporarySignedURL, timestamp } = uploadUrlResult.fetchFileUploadUrl;
      console.log('✅ Upload URL generated');

      // Step 2: Read file and upload to S3
      console.log('📤 Uploading file to S3...');
      const fileBuffer = readFileSync(args.filePath);
      const uploadResponse = await fetch(temporarySignedURL, {
        method: 'PUT',
        body: fileBuffer,
        headers: {
          'Content-Type': 'application/octet-stream',
        },
      });

      if (!uploadResponse.ok) {
        throw new Error(`Failed to upload file to S3: ${uploadResponse.status} ${uploadResponse.statusText}`);
      }
      console.log('✅ File uploaded to S3 successfully');

      // Step 3: Create file document
      console.log('📄 Creating file document...');
      const createDocumentMutation = `
        mutation createFileDocument($input: CreateFileDocumentInput!) {
          createFileDocument(input: $input) {
            fileDocument {
              id
              name
              fileName
              s3Key
              type
              __typename
            }
            __typename
          }
        }
      `;

      const documentVariables = {
        input: {
          fileName: fileName,
          objectId: objectId,
          objectType: args.objectType,
          name: fileName,
          type: args.type,
          permissionType: args.permissionType,
          sourceType: args.type,
          timestamp: timestamp,
        },
      };

      const documentResult = await this.client.request(createDocumentMutation, documentVariables) as any;
      const fileDocument = documentResult.createFileDocument.fileDocument;
      console.log('✅ File document created:', fileDocument.id);

      // Step 4: Update organization theme if requested
      let themeUpdateResult = null;
      if (args.updateTheme && args.objectType === 'ORGANIZATION' && args.type === 'LOGO') {
        console.log('🎨 Updating organization theme...');
        const themeUpdateMutation = `
          mutation updateOrganization($input: UpdateOrganizationInput!) {
            updateOrganization(input: $input) {
              organization {
                id
                __typename
              }
              __typename
            }
          }
        `;

        const themeVariables = {
          input: {
            organizationId: objectId,
            logoFile: {
              fileName: fileName,
              userId: userId,
              generateUniqueFileName: false,
              permissionType: args.permissionType,
            },
          },
        };

        themeUpdateResult = await this.client.request(themeUpdateMutation, themeVariables) as any;
        console.log('✅ Organization theme updated');
      }

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              success: true,
              fileDocument: fileDocument,
              themeUpdate: themeUpdateResult?.updateOrganization || null,
              message: 'File uploaded and processed successfully',
              steps: [
                '1. ✅ Generated upload URL',
                '2. ✅ Uploaded file to S3',
                '3. ✅ Created file document',
                args.updateTheme ? '4. ✅ Updated organization theme' : '4. ⏭️ Skipped theme update',
              ],
            }, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to upload file: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
}
