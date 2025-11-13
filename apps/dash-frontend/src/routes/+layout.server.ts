import { dashBackendUrl } from '$lib/server/dashBackend';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({}) => {
	const [respApps, respNets, clientDomains] = await Promise.all([
		fetch(dashBackendUrl('/api/apps')).then((res) => res.json()),
		fetch(dashBackendUrl('/api/networks')).then((res) => res.json()),
		fetch(dashBackendUrl('/api/links/domains')).then((res) => res.json())
	]);

	console.log(`root layout load apps, networks end`);

	return {
		respApps,
		respNets,
		clientDomains
	};
};
