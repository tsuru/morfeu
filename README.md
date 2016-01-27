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

    export MORFEU_ESEARCH_HOST=localhost
    export POOL_WHITELIST=sample
    export TIME_RANGE_IN_HOURS=48
    export TSURU_APP_PROXY=tsuru-caffeine-proxy
    export TSURU_APP_PROXY_URL=http://url-to-tsuru-caffeine-proxy
    export TSURU_TOKEN=fill me in
    export TSURU_HOST="http://localhost"

Replace the env variables above with the appropriate ones. To get the TSURU_TOKEN run the following commands:

    tsuru login
    tsuru token-show

## standalone dry mode

    python main.py --dry

## daemon mode

    python main.py --daemon

You can also daemonize morfeu and still run it in dry mode.
