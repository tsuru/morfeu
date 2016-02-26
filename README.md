[![Build Status](http://img.shields.io/travis/tsuru/morfeu.svg?style=flat-square)](https://travis-ci.org/tsuru/morfeu)

# install

```sh
mkvirtualenv morfeu
workon morfeu
make deps
make test
```

# run

In order to run morfeu locally you need to export some environment variables

    export MONGODB_ENDPOINT="mongodb://localhost:27017/"
    export TSURU_TOKEN=fill me in
    export TSURU_HOST="http://localhost"

Replace the env variables above with the appropriate ones. To get the TSURU_TOKEN run the following commands:

    tsuru login
    tsuru token-show

All the other configurations stay in the database `config`:

    elastic_search_host="localhost"
    timeout=30
    time_range_in_hours=1
    app_proxy=name of the proxy app
    proxy_url=url for the proxy app
    pools=list of pools of apps that may get asleep, separated by commas
    static_platform_name=name of the static platform
    sleep_time=60
    skip_apps=list of apps that can never get asleep, separated by commas
    domain=domain of apps that can never get asleep

## standalone dry mode

    python main.py --dry

## daemon mode

    python main.py --daemon

You can also daemonize morfeu and still run it in dry mode.
