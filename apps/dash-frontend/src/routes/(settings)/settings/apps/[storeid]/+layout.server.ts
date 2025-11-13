import { dashBackendUrl } from '$lib/server/dashBackend';
import type { LayoutServerLoad } from './$types.js';

export const load: LayoutServerLoad = async ({ params, parent }) => {
	const storeid = params.storeid;
	const appData = await fetch(dashBackendUrl(`/api/apps/${storeid}`)).then((res) =>
		res.json()
	);
	const appLinks = await fetch(
		dashBackendUrl(`/api/apps/${appData.id}/links`)
	).then((res) => res.json());

	const { respNets } = await parent();

	console.log(`root layout load apps, networks end`);

	return {
		appData: appData,
		appLinks: appLinks,
		respNets: respNets
	};
};
