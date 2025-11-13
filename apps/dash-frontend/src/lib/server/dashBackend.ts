import { env } from '$env/dynamic/private';

const baseUrl =
	env.DASH_BACKEND_BASE_URL?.replace(/\/$/, '') ?? 'http://dash-backend:8001';

export function dashBackendUrl(path: string): string {
	if (!path.startsWith('/')) {
		return `${baseUrl}/${path}`;
	}
	return `${baseUrl}${path}`;
}
