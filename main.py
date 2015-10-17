import time
import os
import logging
import sys

import argparse
from ConfigParser import SafeConfigParser

from morfeu.tsuru.app import TsuruApp
from morfeu.tsuru.client import TsuruClient

logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s %(message)s',
                    level=logging.DEBUG,
                    handlers=[logging.StreamHandler(sys.stdout)])

logging.getLogger("requests").setLevel(logging.WARNING)

LOG = logging.getLogger(__name__)

POOL_WHITELIST = os.getenv("POOL_WHITELIST", "").split(',')
TSURU_APP_PROXY = os.getenv("TSURU_APP_PROXY", "")
SLEEP_TIME = int(os.getenv("MORFEU_SLEEP_TIME", "60"))
TIMEOUT = int(os.getenv("MORFEU_TIMEOUT", "30"))

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Morfeu.. put apps to sleep')

    parser.add_argument('--dry', action='store_true',
                        help='Just pretending...')
    parser.add_argument('--daemon', action='store_true',
                        help='Should be daemonized?')

    args = parser.parse_args()
    parser = SafeConfigParser()

    dry = args.dry
    daemon = args.daemon

    tsuru_client = TsuruClient(timeout=TIMEOUT)

    while True:

        try:
            LOG.info("Running morfeu...")

            proxy_app = TsuruApp(name=TSURU_APP_PROXY, timeout=TIMEOUT)
            apps_to_sleep = []
            apps = tsuru_client.list_apps(type="web", domain="")

            for app in apps:
                app_name = app.keys()[0]

                tsuru_app = TsuruApp(name=app_name, dry=dry, timeout=TIMEOUT)
                if tsuru_app.should_go_to_bed():
                    if tsuru_app.pool in POOL_WHITELIST:
                        apps_to_sleep.append(tsuru_app)

            LOG.info("{0} apps to sleep: {1}".format(len(apps_to_sleep), [app.name for app in apps_to_sleep]))

            for app in apps_to_sleep:
                app.stop()
                app.re_route(tsuru_app_proxy=proxy_app)

            if not daemon:
                break

            LOG.info("sleeping for {0} seconds ...".format(SLEEP_TIME))
            time.sleep(SLEEP_TIME)

        except KeyboardInterrupt:
            sys.exit(0)
        except Exception, e:
            LOG.exception("ops... {0}".format(e))
