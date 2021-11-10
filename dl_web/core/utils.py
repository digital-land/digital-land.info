import aiohttp


def create_dict(keys_list, values_list):
    zip_iterator = zip(keys_list, values_list)
    return dict(zip_iterator)


async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()
