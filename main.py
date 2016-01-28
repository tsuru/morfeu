import time
import logging
import sys
import threading

import argparse
from ConfigParser import SafeConfigParser

from morfeu.tsuru.app import TsuruApp
from morfeu.tsuru.client import TsuruClient
from morfeu.settings import TSURU_APP_PROXY, SLEEP_TIME, DOMAIN, APP_WHITELIST

logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s %(message)s',
                    level=logging.DEBUG,
                    handlers=[logging.StreamHandler(sys.stdout)])

logging.getLogger("requests").setLevel(logging.WARNING)

LOG = logging.getLogger(__name__)


def check_sleep(app_name, dry, apps_to_sleep):
    tsuru_app = TsuruApp(name=app_name, dry=dry)
    if tsuru_app.should_go_to_bed():
        apps_to_sleep.append(tsuru_app)


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

    tsuru_client = TsuruClient()

    while True:

        try:
            LOG.info("Running morfeu...")

            proxy_app = TsuruApp(name=TSURU_APP_PROXY)
            apps_to_sleep = []
            apps = tsuru_client.list_apps(type="web", domain=DOMAIN)
            never_sleep = [TSURU_APP_PROXY] + APP_WHITELIST
            apps = [app for app in apps if set(app.keys()).intersection(never_sleep) == set([])]
            threads = []

            for app in apps:
                app_name = app.keys()[0]

                thread = threading.Thread(target=check_sleep, args=(app_name, dry, apps_to_sleep))
                threads.append(thread)
                thread.start()

            [x.join() for x in threads]

            LOG.info("{0} apps to sleep: {1}".format(len(apps_to_sleep), [app.name for app in apps_to_sleep]))

            for app in apps_to_sleep:
                app.stop()

            if not daemon:
                break

            LOG.info("sleeping for {0} seconds ...".format(SLEEP_TIME))
            time.sleep(SLEEP_TIME)

        except KeyboardInterrupt:
            sys.exit(0)
        except Exception, e:
            LOG.exception("ops... {0}".format(e))
