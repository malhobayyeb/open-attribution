## Developing

Once you've created a project and installed dependencies with `npm install` (or `pnpm install` or `yarn`), start a development server:

```bash
npm run dev

# or start the server and open the app in a new browser tab
npm run dev -- --open
```

## Building

To create a production version of your app:

```bash
npm run build
```

You can preview the production build with `npm run preview`.

> To deploy your app, you may need to install an [adapter](https://kit.svelte.dev/docs/adapters) for your target environment.

## Configuration

The frontend calls the dashboard backend directly when rendering server routes.
Set `DASH_BACKEND_BASE_URL` (copy `.env.example` to `.env`) to point at the
appropriate backend URL for your environment; it defaults to
`http://dash-backend:8001` for the Docker stack.
