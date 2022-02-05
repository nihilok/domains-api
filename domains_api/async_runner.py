import asyncio
import sys
from domains_api.ip_changer import IPChanger

checker = IPChanger()
checker.load_user()

async def run_at_interval(interval: int):
    while True:
        checker.run()
        await asyncio.sleep(interval)

if __name__ == "__main__":
    try:
        asyncio.run(run_at_interval(int(sys.argv[1])))
    except IndexError:
        print("usage: 'domainsd 60' (check every 60 seconds)")
        sys.exit(1)
