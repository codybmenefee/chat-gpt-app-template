import { ConfigManager } from '../config/config-manager.js';

export class ValidationUtils {
  private configManager: ConfigManager;

  constructor(configManager: ConfigManager) {
    this.configManager = configManager;
  }

  validateConfiguration(): void {
    if (!this.configManager.isConfigured()) {
      throw new Error('MCP server is not configured. Use config_set to configure graphqlEndpoint and apiKey.');
    }
  }

  validateFullConfiguration(): void {
    if (!this.configManager.isFullyConfigured()) {
      const config = this.configManager.getConfig();
      const missing = [];
      
      if (!config.organizationId) missing.push('organizationId');
      if (!config.userId) missing.push('userId');
      
      throw new Error(`MCP server is not fully configured. Missing: ${missing.join(', ')}. Use config_set to configure these values.`);
    }
  }

  getOrganizationId(): string {
    this.validateFullConfiguration();
    return this.configManager.getOrganizationId();
  }

  getUserId(): string {
    this.validateFullConfiguration();
    return this.configManager.getUserId();
  }

  validateOrganizationId(organizationId?: string): string {
    if (organizationId) {
      return organizationId;
    }
    return this.getOrganizationId();
  }

  validateUserId(userId?: string): string {
    if (userId) {
      return userId;
    }
    return this.getUserId();
  }
}
