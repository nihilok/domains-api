import asyncio
import sys
from domains_api.ip_changer import IPChanger

checker = IPChanger()


async def run_at_interval(interval: int):
    if type(interval) is not int:
        raise ValueError("interval must be an integer")
    while True:
        try:
            checker.run()
        except Exception as e:
            checker.fh.log(f"{e.__class__.__name__} {e.__str__()} [{e.__cause__}]", "error")
        await asyncio.sleep(interval*60)


if __name__ == "__main__":
    try:
        asyncio.run(run_at_interval(int(sys.argv[1])))
    except (IndexError, ValueError):
        print("usage: 'domainsd 60' (check every 60 minutes)")
        sys.exit(1)
