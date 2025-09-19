# Team Installation Command

## Share this with your team:

```bash
curl -fsSL https://raw.githubusercontent.com/codybmenefee/one-agent/main/install.sh | bash
```

## Or for local installation:

```bash
cd /path/to/one-agent && ./install.sh
```

## What team members need to do:

1. **Run the command above** in their terminal
2. **Restart Cursor** after installation
3. **Set up `.env.local`** with their API credentials:
   ```env
   API_KEY=their-bearer-token
   ORGANIZATION_ID=your-org-id
   USER_ID=their-user-id
   ```

## Prerequisites:
- Node.js 22.0.0 or higher
- Cursor IDE installed

That's it! The installer handles everything else automatically.
