# OneAgent MCP Server - Deployment Guide

This guide will help you deploy the OneAgent MCP Server installer to Vercel, making it easy for your team to install the MCP server with a simple click.

## Prerequisites

- Node.js 22+ installed
- Vercel CLI installed (`npm install -g vercel`)
- Git repository with your code
- Vercel account

## Quick Deployment

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Login to Vercel

```bash
vercel login
```

### 3. Deploy the Installer

```bash
# From the project root
npm run deploy:installer
```

### 4. Get Your URL

After deployment, Vercel will provide you with a URL like:
- `https://oneagent-mcp-installer.vercel.app`
- `https://your-project-name.vercel.app`

## Custom Domain (Optional)

### 1. Add Custom Domain in Vercel Dashboard

1. Go to your project in the Vercel dashboard
2. Click on "Settings" → "Domains"
3. Add your custom domain (e.g., `install.oneagent.com`)

### 2. Update DNS

Add a CNAME record pointing to your Vercel deployment:
```
install.oneagent.com → cname.vercel-dns.com
```

## Team Distribution

### 1. Share the Installer URL

Send your team the installer URL:
```
https://your-project.vercel.app
```

### 2. Team Installation Process

Your team members will:
1. Visit the installer URL
2. Fill out the configuration form
3. Click "Install" to generate MCP configuration
4. Follow the provided instructions

### 3. Update Documentation

Update your team documentation with:
- The installer URL
- Installation instructions
- Troubleshooting guide

## Advanced Configuration

### Environment Variables

If you need to customize the installer, you can set environment variables in Vercel:

1. Go to your project settings
2. Click on "Environment Variables"
3. Add any custom configuration

### Custom Styling

To customize the installer appearance:

1. Edit `installer/index.html` and `installer/landing.html`
2. Modify the CSS styles
3. Redeploy with `npm run deploy:installer`

### Custom Functionality

To add new features:

1. Edit `installer/installer.js`
2. Add new configuration fields
3. Update the installation logic
4. Redeploy

## Monitoring

### Vercel Analytics

Enable Vercel Analytics to track:
- Installer page views
- Installation success rates
- User engagement

### Error Monitoring

Consider adding error monitoring:
- Sentry for JavaScript errors
- Vercel's built-in error tracking
- Custom analytics

## Security Considerations

### HTTPS Only

The installer requires HTTPS for:
- File System Access API
- Secure credential handling
- Modern browser features

### Credential Security

- All configuration is processed client-side
- No credentials are sent to external servers
- Configuration files are generated locally

### Content Security Policy

Consider adding CSP headers in `vercel.json`:

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        }
      ]
    }
  ]
}
```

## Troubleshooting

### Deployment Issues

1. **Build Failures**:
   - Check that all files are committed
   - Verify Vercel CLI is up to date
   - Check for syntax errors in HTML/JS

2. **Routing Issues**:
   - Verify `vercel.json` configuration
   - Check file paths in routes
   - Test all routes after deployment

3. **File Not Found**:
   - Ensure all files are in the `installer/` directory
   - Check file names and extensions
   - Verify Vercel build configuration

### Installation Issues

1. **File System Access Not Working**:
   - Ensure HTTPS is enabled
   - Check browser compatibility
   - Verify user permissions

2. **Configuration Not Saving**:
   - Check browser console for errors
   - Verify file path permissions
   - Try manual installation mode

## Maintenance

### Regular Updates

1. **Update Dependencies**:
   ```bash
   npm update
   npm run deploy:installer
   ```

2. **Update Installer**:
   - Modify installer files
   - Test locally with `npm run preview:installer`
   - Deploy with `npm run deploy:installer`

3. **Monitor Performance**:
   - Check Vercel dashboard for metrics
   - Monitor error rates
   - Update as needed

### Version Management

Consider using Vercel's preview deployments for testing:
```bash
vercel  # Creates preview deployment
vercel --prod  # Deploys to production
```

## Support

For deployment issues:

1. Check Vercel dashboard for build logs
2. Review browser console for client-side errors
3. Test locally with `npm run preview:installer`
4. Contact Vercel support if needed

## Cost

Vercel's free tier includes:
- 100GB bandwidth per month
- Unlimited static deployments
- Custom domains
- Automatic HTTPS

For high-traffic deployments, consider upgrading to Vercel Pro.
