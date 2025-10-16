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

export class GraphQLTools {
  private client: GraphQLClient;
  private tools: Tool[] = [];
  private configManager: ConfigManager;
  private failedAttempts: Map<string, { count: number; lastAttempt: number; errors: string[] }> = new Map();

  constructor(client: GraphQLClient, configManager: ConfigManager) {
    this.client = client;
    this.configManager = configManager;
    this.initializeTools();
  }

  private initializeTools() {
    this.tools = [
      {
        name: 'update_organization_theme',
        description: 'Update organization theme, branding, and visual design settings. PRIMARY tool for organization logo uploads and theme customization. Handles colors, typography, layout, and all visual branding elements. Logo uploads are automatically linked to the organization. If organizationId is not provided, uses the configured organization ID from .env.local.',
        inputSchema: z.object({
          organizationId: z.string().min(1, 'Organization ID is required').optional(),
          
          // Branding
          faviconLink: z.string().optional(),
          browserTabTitle: z.string().optional(),
          
          // Logo upload
          logoFile: z.object({
            fileName: z.string().min(1, 'File name is required'),
            filePath: z.string().min(1, 'File path is required for logo upload'),
            userId: z.string().min(1, 'User ID is required for logo upload'),
            generateUniqueFileName: z.boolean().default(true),
            permissionType: z.enum(['PUBLIC', 'PRIVATE', 'RESTRICTED']).default('PUBLIC'),
          }).optional(),
          
          // Theme tokens - comprehensive schema supporting all GraphQL attributes
          themeTokens: z.object({
            // Reference tokens (design system foundation)
            ref: z.object({
              palette: z.object({
                primary50: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
                supportOne50: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
                supportTwo50: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
                supportThree50: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
                supportFour50: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
                supportFive50: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
                supportSix50: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
              }).optional(),
            }).optional(),
            
            // Component tokens (how ref tokens are applied to components)
            comp: z.object({
              layout: z.object({
                backgroundColor: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
                textColor: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
              }).optional(),
              card: z.object({
                borderRadius: z.string().regex(/^\d+px$/, 'Must be valid CSS border radius (e.g., "16px")').optional(),
              }).optional(),
              button: z.object({
                borderRadius: z.string().regex(/^\d+px$/, 'Must be valid CSS border radius (e.g., "2px")').optional(),
                lg: z.object({
                  height: z.string().regex(/^\d+px$/, 'Must be valid CSS height (e.g., "40px")').optional(),
                  fontSize: z.string().regex(/^\d+px$/, 'Must be valid CSS font size (e.g., "16px")').optional(),
                }).optional(),
                filled: z.object({
                  primary: z.object({
                    hovered: z.object({
                      container: z.object({
                        color: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
                      }).optional(),
                      text: z.object({
                        color: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
                      }).optional(),
                    }).optional(),
                    enabled: z.object({
                      container: z.object({
                        color: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
                      }).optional(),
                      text: z.object({
                        color: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
                      }).optional(),
                    }).optional(),
                  }).optional(),
                }).optional(),
                outlined: z.object({
                  primary: z.object({
                    enabled: z.object({
                      container: z.object({
                        color: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
                      }).optional(),
                      text: z.object({
                        color: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
                      }).optional(),
                    }).optional(),
                  }).optional(),
                }).optional(),
              }).optional(),
              tabNav: z.object({
                background: z.object({
                  active: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
                }).optional(),
              }).optional(),
              selectionChip: z.object({
                borderRadius: z.string().regex(/^\d+px$/, 'Must be valid CSS border radius (e.g., "4px")').optional(),
                background: z.object({
                  active: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
                }).optional(),
              }).optional(),
              textField: z.object({
                textColor: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
                labelColor: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
                fontSize: z.string().regex(/^\d+px$/, 'Must be valid CSS font size (e.g., "16px")').optional(),
                borderColor: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
                errorColor: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
              }).optional(),
              helpText: z.object({
                errorColor: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
              }).optional(),
              statusBar: z.object({
                containerColor: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
                borderColor: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
                borderRadius: z.number().optional(),
                activeColor: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
              }).optional(),
              typography: z.object({
                headingSmall: z.object({
                  fontFamily: z.string().optional(),
                  fontSize: z.string().regex(/^\d+px$/, 'Must be valid CSS font size (e.g., "24px")').optional(),
                }).optional(),
                displayLargeVariant: z.object({
                  fontFamily: z.string().optional(),
                  fontSize: z.string().regex(/^\d+px$/, 'Must be valid CSS font size (e.g., "42px")').optional(),
                }).optional(),
                bodySmall: z.object({
                  fontSize: z.string().regex(/^\d+px$/, 'Must be valid CSS font size (e.g., "20px")').optional(),
                  fontWeight: z.number().optional(),
                  lineHeight: z.string().regex(/^\d+px$/, 'Must be valid CSS line height (e.g., "16px")').optional(),
                  letterSpacing: z.string().regex(/^\d+\.?\d*px$/, 'Must be valid CSS letter spacing (e.g., "0.25px")').optional(),
                }).optional(),
              }).optional(),
              lineChart: z.object({
                tension: z.number().optional(),
                color: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
                showAxis: z.boolean().optional(),
              }).optional(),
            }).optional(),
            
            // System tokens
            sys: z.object({
              color: z.object({
                background: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be valid hex color').optional(),
              }).optional(),
              borderRadius: z.object({
                xl: z.string().regex(/^\d+px$/, 'Must be valid CSS border radius (e.g., "4px")').optional(),
              }).optional(),
              elevation: z.object({
                surface: z.string().optional(), // Complex shadow values like "2px 2px 10px 2px rgba(0, 0, 0, 0.10), 0px 1px 2px 0px rgba(0, 0, 0, 0.10)"
              }).optional(),
            }).optional(),
          }).optional(),
          
          // Additional theme settings
          theme: z.record(z.any()).optional(),
        }),
        handler: this.updateOrganizationTheme.bind(this),
      },
      {
        name: 'list_organization_logos',
        description: 'List all logo files associated with an organization. Useful for verifying logo uploads and managing multiple logos.',
        inputSchema: z.object({
          organizationId: z.string().min(1, 'Organization ID is required').optional(),
          limit: z.number().min(1).max(50).default(10).optional(),
        }),
        handler: this.listOrganizationLogos.bind(this),
      },
      {
        name: 'get_logo_download_url',
        description: 'Get the download URL for a specific logo file. Useful for verifying logo accessibility and getting the URL to display the logo.',
        inputSchema: z.object({
          fileDocumentId: z.string().min(1, 'File document ID is required'),
        }),
        handler: this.getLogoDownloadUrl.bind(this),
      },
      {
        name: 'verify_organization_logo',
        description: 'Verify that an organization has a logo and get its details. Returns the most recent logo file information.',
        inputSchema: z.object({
          organizationId: z.string().min(1, 'Organization ID is required').optional(),
        }),
        handler: this.verifyOrganizationLogo.bind(this),
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

    console.log('DEBUG: Raw args before validation:', JSON.stringify(args, null, 2));
    
    try {
      const validatedArgs = tool.inputSchema.parse(args);
      console.log('DEBUG: Validated args after validation:', JSON.stringify(validatedArgs, null, 2));
      
      // Clear failed attempts on successful validation
      this.clearFailedAttempts(name);
      
      return await tool.handler(validatedArgs);
    } catch (validationError) {
      // Track failed attempts for loop detection
      this.trackFailedAttempt(name, validationError instanceof Error ? validationError.message : String(validationError));
      
      // Check if we're in a loop (3+ failed attempts in last 2 minutes)
      const attemptInfo = this.failedAttempts.get(name);
      if (attemptInfo && attemptInfo.count >= 3 && (Date.now() - attemptInfo.lastAttempt) < 120000) {
        const errorMessage = `LOOP DETECTED: This tool has failed ${attemptInfo.count} times in the last 2 minutes with similar errors. Please STOP retrying and ask the user for clarification or different parameters. Recent errors: ${attemptInfo.errors.slice(-3).join('; ')}`;
        throw new Error(errorMessage);
      }
      
      // Re-throw the original validation error
      throw validationError;
    }
  }

  private trackFailedAttempt(toolName: string, errorMessage: string) {
    const now = Date.now();
    const existing = this.failedAttempts.get(toolName);
    
    if (existing) {
      // Reset if more than 5 minutes have passed
      if (now - existing.lastAttempt > 300000) {
        this.failedAttempts.set(toolName, {
          count: 1,
          lastAttempt: now,
          errors: [errorMessage]
        });
      } else {
        // Increment count and add error
        existing.count++;
        existing.lastAttempt = now;
        existing.errors.push(errorMessage);
        // Keep only last 5 errors
        if (existing.errors.length > 5) {
          existing.errors = existing.errors.slice(-5);
        }
      }
    } else {
      this.failedAttempts.set(toolName, {
        count: 1,
        lastAttempt: now,
        errors: [errorMessage]
      });
    }
  }

  private clearFailedAttempts(toolName: string) {
    this.failedAttempts.delete(toolName);
  }

  private async updateOrganizationTheme(args: {
    organizationId?: string;
    faviconLink?: string;
    browserTabTitle?: string;
    logoFile?: {
      fileName: string;
      filePath: string;
      userId: string;
      generateUniqueFileName: boolean;
      permissionType: 'PUBLIC' | 'PRIVATE' | 'RESTRICTED';
    };
    themeTokens?: {
      ref?: {
        palette?: {
          primary50?: string;
          supportOne50?: string;
          supportTwo50?: string;
          supportThree50?: string;
          supportFour50?: string;
          supportFive50?: string;
          supportSix50?: string;
        };
      };
      comp?: {
        layout?: {
          backgroundColor?: string;
          textColor?: string;
        };
        card?: {
          borderRadius?: string;
        };
        button?: {
          borderRadius?: string;
          lg?: {
            height?: string;
            fontSize?: string;
          };
          filled?: {
            primary?: {
              hovered?: {
                container?: {
                  color?: string;
                };
                text?: {
                  color?: string;
                };
              };
              enabled?: {
                container?: {
                  color?: string;
                };
                text?: {
                  color?: string;
                };
              };
            };
          };
          outlined?: {
            primary?: {
              enabled?: {
                container?: {
                  color?: string;
                };
                text?: {
                  color?: string;
                };
              };
            };
          };
        };
        tabNav?: {
          background?: {
            active?: string;
          };
        };
        selectionChip?: {
          borderRadius?: string;
          background?: {
            active?: string;
          };
        };
        textField?: {
          textColor?: string;
          labelColor?: string;
          fontSize?: string;
          borderColor?: string;
          errorColor?: string;
        };
        helpText?: {
          errorColor?: string;
        };
        statusBar?: {
          containerColor?: string;
          borderColor?: string;
          borderRadius?: number;
          activeColor?: string;
        };
        typography?: {
          headingSmall?: {
            fontFamily?: string;
            fontSize?: string;
          };
          displayLargeVariant?: {
            fontFamily?: string;
            fontSize?: string;
          };
          bodySmall?: {
            fontSize?: string;
            fontWeight?: number;
            lineHeight?: string;
            letterSpacing?: string;
          };
        };
        lineChart?: {
          tension?: number;
          color?: string;
          showAxis?: boolean;
        };
      };
      sys?: {
        color?: {
          background?: string;
        };
        borderRadius?: {
          xl?: string;
        };
        elevation?: {
          surface?: string;
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

          // Step 2: Upload file to S3
          console.log('📤 Uploading logo file to S3...');
          const fileBuffer = readFileSync(args.logoFile.filePath);
          const uploadResponse = await fetch(temporarySignedURL, {
            method: 'PUT',
            body: fileBuffer,
            headers: {
              'Content-Type': 'application/octet-stream',
            },
          });

          if (!uploadResponse.ok) {
            throw new Error(`Failed to upload logo file to S3: ${uploadResponse.status} ${uploadResponse.statusText}`);
          }
          console.log('✅ Logo file uploaded to S3 successfully');

          // Step 3: Create file document
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
      console.log('DEBUG: args.themeTokens received:', JSON.stringify(args.themeTokens, null, 2));
      console.log('DEBUG: args.themeTokens type:', typeof args.themeTokens);
      console.log('DEBUG: args.themeTokens keys:', args.themeTokens ? Object.keys(args.themeTokens) : 'undefined');
      
      // Check specifically for sys and elevation
      if (args.themeTokens?.sys) {
        console.log('DEBUG: args.themeTokens.sys found:', JSON.stringify(args.themeTokens.sys, null, 2));
        if (args.themeTokens.sys.elevation) {
          console.log('DEBUG: args.themeTokens.sys.elevation found:', JSON.stringify(args.themeTokens.sys.elevation, null, 2));
        } else {
          console.log('DEBUG: args.themeTokens.sys.elevation NOT FOUND');
        }
      } else {
        console.log('DEBUG: args.themeTokens.sys NOT FOUND');
      }
      
      const mutationInput = {
        organizationId: organizationId,
        faviconLink: args.faviconLink || null,
        browserTabTitle: args.browserTabTitle || null,
        themeTokens: args.themeTokens || {},
        theme: args.theme || {}
      };
      
      console.log('DEBUG: mutationInput.themeTokens:', JSON.stringify(mutationInput.themeTokens, null, 2));
      
      // Check mutation input specifically for sys and elevation
      if (mutationInput.themeTokens?.sys) {
        console.log('DEBUG: mutationInput.themeTokens.sys found:', JSON.stringify(mutationInput.themeTokens.sys, null, 2));
        if (mutationInput.themeTokens.sys.elevation) {
          console.log('DEBUG: mutationInput.themeTokens.sys.elevation found:', JSON.stringify(mutationInput.themeTokens.sys.elevation, null, 2));
        } else {
          console.log('DEBUG: mutationInput.themeTokens.sys.elevation NOT FOUND IN MUTATION INPUT');
        }
      } else {
        console.log('DEBUG: mutationInput.themeTokens.sys NOT FOUND IN MUTATION INPUT');
      }

      const mutation = `
        mutation updateOrganization($input: UpdateOrganizationInput!) {
          updateOrganization(input: $input) {
            organization {
              id
              name
              __typename
            }
            __typename
          }
        }
      `;

      console.log('DEBUG: About to send GraphQL request with variables:', JSON.stringify({ input: mutationInput }, null, 2));
      console.log('DEBUG: GraphQL variables input.themeTokens:', JSON.stringify(mutationInput.themeTokens, null, 2));
      console.log('DEBUG: GraphQL variables input.themeTokens.sys:', JSON.stringify(mutationInput.themeTokens?.sys, null, 2));
      console.log('DEBUG: GraphQL variables input.themeTokens.sys.elevation:', JSON.stringify(mutationInput.themeTokens?.sys?.elevation, null, 2));

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

  private async listOrganizationLogos(args: {
    organizationId?: string;
    limit?: number;
  }) {
    try {
      const organizationId = args.organizationId || this.configManager.getOrganizationId();
      const limit = args.limit || 10;

      if (!organizationId) {
        throw new Error('Organization ID is required. Set ORGANIZATION_ID environment variable or provide organizationId parameter.');
      }

      const query = `
        query fetchFileDocuments($filter: FileDocumentQueryFilter) {
          fetchFileDocuments(
            input: {
              filter: $filter
              pagination: { 
                perPage: ${limit}, 
                sortDesc: true, 
                sortField: "createdAt" 
              }
            }
          ) {
            fileDocuments {
              id
              name
              fileName
              type
              objectType
              objectId
              createdAt
              __typename
            }
            __typename
          }
        }
      `;

      const variables = {
        filter: {
          organizationId: organizationId,
          types: ["LOGO"],
          objectTypes: ["ORGANIZATION"]
        }
      };

      const result = await this.client.request(query, variables) as any;
      const logos = result.fetchFileDocuments.fileDocuments;

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              success: true,
              organizationId: organizationId,
              logoCount: logos.length,
              logos: logos.map((logo: any) => ({
                id: logo.id,
                name: logo.name,
                fileName: logo.fileName,
                createdAt: logo.createdAt,
                isMostRecent: logos.indexOf(logo) === 0
              })),
              message: `Found ${logos.length} logo(s) for organization ${organizationId}`,
              instructions: [
                'Use get_logo_download_url with a logo ID to get the download URL',
                'Use verify_organization_logo to check the most recent logo',
                'The first logo in the list is the most recent'
              ]
            }, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to list organization logos: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  private async getLogoDownloadUrl(args: {
    fileDocumentId: string;
  }) {
    try {
      const query = `
        query fetchFileDocumentDownloadUrl($fileDocumentId: ObjectID!) {
          fetchFileDocument(fileDocumentId: $fileDocumentId) {
            fileDocument {
              id
              name
              fileName
              downloadUrl
              mediaType
              type
              objectType
              objectId
              __typename
            }
            __typename
          }
        }
      `;

      const variables = {
        fileDocumentId: args.fileDocumentId
      };

      const result = await this.client.request(query, variables) as any;
      const fileDocument = result.fetchFileDocument.fileDocument;

      if (!fileDocument) {
        throw new Error(`Logo file not found with ID: ${args.fileDocumentId}`);
      }

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              success: true,
              fileDocument: {
                id: fileDocument.id,
                name: fileDocument.name,
                fileName: fileDocument.fileName,
                downloadUrl: fileDocument.downloadUrl,
                mediaType: fileDocument.mediaType,
                type: fileDocument.type,
                objectType: fileDocument.objectType,
                objectId: fileDocument.objectId
              },
              message: 'Logo download URL retrieved successfully',
              instructions: [
                'Use the downloadUrl to display the logo in your application',
                'The URL is a signed S3 URL that expires after 5 minutes',
                'For permanent access, store the fileDocument.id and call this tool again'
              ]
            }, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to get logo download URL: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  private async verifyOrganizationLogo(args: {
    organizationId?: string;
  }) {
    try {
      const organizationId = args.organizationId || this.configManager.getOrganizationId();

      if (!organizationId) {
        throw new Error('Organization ID is required. Set ORGANIZATION_ID environment variable or provide organizationId parameter.');
      }

      // First, get the most recent logo
      const listQuery = `
        query fetchFileDocuments($filter: FileDocumentQueryFilter) {
          fetchFileDocuments(
            input: {
              filter: $filter
              pagination: { 
                perPage: 1, 
                sortDesc: true, 
                sortField: "createdAt" 
              }
            }
          ) {
            fileDocuments {
              id
              name
              fileName
              type
              objectType
              objectId
              createdAt
              __typename
            }
            __typename
          }
        }
      `;

      const listVariables = {
        filter: {
          organizationId: organizationId,
          types: ["LOGO"],
          objectTypes: ["ORGANIZATION"]
        }
      };

      const listResult = await this.client.request(listQuery, listVariables) as any;
      const logos = listResult.fetchFileDocuments.fileDocuments;

      if (logos.length === 0) {
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                success: false,
                organizationId: organizationId,
                hasLogo: false,
                message: 'No logo found for this organization',
                instructions: [
                  'Use update_organization_theme with logoFile parameter to upload a logo',
                  'Make sure to provide both fileName and filePath in the logoFile object'
                ]
              }, null, 2),
            },
          ],
        };
      }

      const mostRecentLogo = logos[0];

      // Get the download URL for the most recent logo
      const downloadQuery = `
        query fetchFileDocumentDownloadUrl($fileDocumentId: ObjectID!) {
          fetchFileDocument(fileDocumentId: $fileDocumentId) {
            fileDocument {
              id
              name
              fileName
              downloadUrl
              mediaType
              type
              objectType
              objectId
              __typename
            }
            __typename
          }
        }
      `;

      const downloadVariables = {
        fileDocumentId: mostRecentLogo.id
      };

      const downloadResult = await this.client.request(downloadQuery, downloadVariables) as any;
      const fileDocument = downloadResult.fetchFileDocument.fileDocument;

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              success: true,
              organizationId: organizationId,
              hasLogo: true,
              logo: {
                id: fileDocument.id,
                name: fileDocument.name,
                fileName: fileDocument.fileName,
                downloadUrl: fileDocument.downloadUrl,
                mediaType: fileDocument.mediaType,
                type: fileDocument.type,
                objectType: fileDocument.objectType,
                objectId: fileDocument.objectId,
                createdAt: mostRecentLogo.createdAt
              },
              message: 'Organization logo verified successfully',
              instructions: [
                'The logo is properly linked to the organization',
                'Use the downloadUrl to display the logo',
                'Use list_organization_logos to see all logos for this organization'
              ]
            }, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to verify organization logo: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
}
