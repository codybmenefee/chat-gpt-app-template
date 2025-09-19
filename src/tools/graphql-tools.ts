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
        name: 'update_organization_theme',
        description: 'Update organization theme, branding, and visual design settings. PREFERRED tool for uploading organization logos and updating branding elements. If organizationId is not provided, uses the configured organization ID from .env.local.',
        inputSchema: z.object({
          organizationId: z.string().min(1, 'Organization ID is required').optional(),
          
          // Branding
          faviconLink: z.string().optional(),
          browserTabTitle: z.string().optional(),
          
          // Logo upload
          logoFile: z.object({
            fileName: z.string().min(1, 'File name is required'),
            userId: z.string().min(1, 'User ID is required for logo upload'),
            generateUniqueFileName: z.boolean().default(true),
            permissionType: z.enum(['PUBLIC', 'PRIVATE', 'RESTRICTED']).default('PUBLIC'),
          }).optional(),
          
          // Theme tokens - exactly as defined in your example
          themeTokens: z.object({
            // Reference tokens (design system foundation)
            ref: z.object({
              palette: z.object({
                primary50: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
              }).optional(),
            }).optional(),
            
            // Component tokens (how ref tokens are applied to components)
            comp: z.object({
              layout: z.object({
                backgroundColor: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
              }).optional(),
              card: z.object({
                borderRadius: z.string().regex(/^\d+px$/, 'Must be valid CSS border radius (e.g., "16px")').optional(),
              }).optional(),
              button: z.object({
                borderRadius: z.string().regex(/^\d+px$/, 'Must be valid CSS border radius (e.g., "100px")').optional(),
              }).optional(),
            }).optional(),
            
            // System tokens
            sys: z.object({
              color: z.object({
                background: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
              }).optional(),
            }).optional(),
          }).optional(),
          
          // Additional theme settings
          theme: z.record(z.any()).optional(),
        }),
        handler: this.updateOrganizationTheme.bind(this),
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
    if (args.organizationId && (args.organizationId.includes('your_') || args.organizationId.includes('placeholder') || args.organizationId.includes('_here'))) {
      throw new Error('Invalid organization ID provided. Please omit the organizationId parameter to use the configured value, or provide a valid organization ID.');
    }

    const validatedArgs = tool.inputSchema.parse(args);
    return await tool.handler(validatedArgs);
  }

  private async updateOrganizationTheme(args: {
    organizationId?: string;
    faviconLink?: string;
    browserTabTitle?: string;
    logoFile?: {
      fileName: string;
      userId: string;
      generateUniqueFileName: boolean;
      permissionType: 'PUBLIC' | 'PRIVATE' | 'RESTRICTED';
    };
    themeTokens?: {
      ref?: {
        palette?: {
          primary50?: string;
        };
      };
      comp?: {
        layout?: {
          backgroundColor?: string;
        };
        card?: {
          borderRadius?: string;
        };
        button?: {
          borderRadius?: string;
        };
      };
      sys?: {
        color?: {
          background?: string;
        };
      };
    };
    theme?: Record<string, any>;
  }) {
    try {
      // Use configuration as fallbacks
      const organizationId = args.organizationId || this.configManager.getOrganizationId();
      const userId = args.logoFile?.userId || this.configManager.getUserId();


      if (!organizationId) {
        throw new Error('Organization ID is required. Set ORGANIZATION_ID environment variable or provide organizationId parameter.');
      }

      let logoUploadResult = null;
      
      // Handle logo upload if provided
      if (args.logoFile) {
        if (!userId) {
          throw new Error('User ID is required for logo upload. Set USER_ID environment variable or provide userId in logoFile parameter.');
        }

        try {
          // Step 1: Get upload URL
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
              objectType: 'ORGANIZATION',
              objectId: organizationId,
              fileName: args.logoFile.fileName,
              type: 'LOGO',
              userId: userId,
              generateUniqueFileName: args.logoFile.generateUniqueFileName,
            },
          };

          const uploadUrlResponse = await this.client.request(uploadUrlQuery, uploadUrlVariables) as any;
          const { temporarySignedURL, timestamp } = uploadUrlResponse.fetchFileUploadUrl;

          // Step 2: Create file document
          const createFileMutation = `
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

          const createFileVariables = {
            input: {
              fileName: args.logoFile.fileName,
              objectId: organizationId,
              objectType: 'ORGANIZATION',
              name: args.logoFile.fileName,
              type: 'LOGO',
              permissionType: args.logoFile.permissionType,
              sourceType: 'LOGO',
              timestamp: timestamp,
            },
          };

          const createFileResponse = await this.client.request(createFileMutation, createFileVariables) as any;
          logoUploadResult = {
            uploadUrl: temporarySignedURL,
            fileDocument: createFileResponse.createFileDocument.fileDocument,
            timestamp: timestamp,
          };
        } catch (logoError) {
          console.warn('Logo upload failed, continuing with theme update:', logoError);
          // Continue with theme update even if logo upload fails
        }
      }

      // Build the mutation input object with proper nesting
      const mutationInput = {
        organizationId: organizationId,
        faviconLink: args.faviconLink || null,
        browserTabTitle: args.browserTabTitle || null,
        themeTokens: args.themeTokens || {},
        theme: args.theme || {}
      };

      const mutation = `
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

      const result = await this.client.request(mutation, { input: mutationInput }) as any;

      const response: any = {
        success: true,
        organizationId: result.updateOrganization.organization.id,
        message: 'Organization theme updated successfully',
        updatedFields: Object.keys(args).filter(key => key !== 'organizationId' && (args as any)[key] !== undefined)
      };

      // Include logo upload information if provided
      if (logoUploadResult) {
        response.logoUpload = {
          uploadUrl: logoUploadResult.uploadUrl,
          fileDocumentId: logoUploadResult.fileDocument.id,
          fileName: logoUploadResult.fileDocument.fileName,
          instructions: [
            '1. Upload your logo file to the provided uploadUrl using a PUT request',
            '2. The logo will be automatically associated with the organization',
            '3. Use the fileDocumentId to reference the uploaded logo in other operations',
          ],
        };
      }

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(response, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new Error(`Theme update failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
}
