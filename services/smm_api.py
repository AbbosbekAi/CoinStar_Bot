import aiohttp


async def send_order(service_code: str, link: str, quantity: int, api_url: str = None, api_key: str = None):
    """
    SMM panel API'siga buyurtma yuboradi.
    Ko'pchilik panellar quyidagi parametrlarni qabul qiladi:
    key, action, service, link, quantity
    """
    if not api_url or not api_key:
        return None, "SMM API sozlanmagan"

    params = {
        "key": api_key,
        "action": "add",
        "service": service_code,
        "link": link,
        "quantity": quantity,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, data=params, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                data = await resp.json()
                return data, None
    except aiohttp.ClientError as e:
        return None, f"API xatosi: {e}"
    except Exception as e:
        return None, str(e)