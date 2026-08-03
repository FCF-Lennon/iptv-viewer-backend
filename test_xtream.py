import asyncio
from app.services.xtream_service import XtreamClient
from app.core.config import setting
from app.core.http_client import get_http_client

async def main():
    client = XtreamClient(
        host=setting.XTREAM_HOST,
        username=setting.XTREAM_USERNAME,
        password=setting.XTREAM_PASSWORD
    )
    
    # fetch raw Live streams
    live_data = await client._get("get_live_streams")
    if live_data:
        # Get first stream with an epg_channel_id
        epg_stream = next((item for item in live_data if item.get('epg_channel_id')), None)
        if epg_stream:
            stream_id = epg_stream.get('stream_id')
            epg_id = epg_stream.get('epg_channel_id')
            print(f"Found stream with EPG ID: {epg_stream.get('name')} (Stream ID: {stream_id}, EPG ID: {epg_id})")
            
            # Try to get short EPG
            print("\nTesting get_short_epg...")
            epg_data = await client._get("get_short_epg", {"stream_id": stream_id})
            print(f"Short EPG Response: {epg_data}")
        else:
            print("No live stream with epg_channel_id found.")
            
    # close http client
    await get_http_client().aclose()

if __name__ == "__main__":
    asyncio.run(main())
