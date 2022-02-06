import asyncio
import sys
from domains_api.ip_changer import IPChanger


async def _run_check_log_exceptions():
    checker = IPChanger()
    try:
        checker.run()
    except Exception as e:
        checker.fh.log(
            f"{e.__class__.__name__} {e.__str__()} [{e.__cause__}]", "error"
        )
    del checker


async def run_at_interval(interval: int):
    if type(interval) is not int:
        raise ValueError("interval must be an integer")
    interval *= 60
    while True:
        await _run_check_log_exceptions()
        await asyncio.sleep(interval)


if __name__ == "__main__":
    try:
        asyncio.run(run_at_interval(int(sys.argv[1])))
    except (IndexError, ValueError):
        print("usage: 'domainsd 60' (check every 60 minutes)")
        sys.exit(1)
