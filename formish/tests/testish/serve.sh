# Change to the testish root directory.
cd `dirname $0`

case "$1" in
  start)
    ./run paster serve \
        --daemon \
        --pid-file=./log/live.pid \
        --log-file=./log/live.log \
                   ./live.ini \
        start
    ;;
  stop)
    ./run paster serve \
        --daemon \
        --pid-file=./log/live.pid \
        --log-file=./log/live.log \
                   ./live.ini \
        stop
    ;;
  restart)
    ./run paster serve \
        --daemon \
        --pid-file=./log/live.pid \
        --log-file=./log/live.log \
                   ./live.ini \
        restart
    ;;
  run)
    ./run paster serve \
        --log-file=./log/live.log \
                   ./live.ini
    ;;
  start-dev)
    ./run paster serve \
        --daemon \
        --pid-file=./log/development.pid \
        --log-file=./log/development.log \
                   ./development.ini \
        start
    ;;
  stop-dev)
    ./run paster serve \
        --daemon \
        --pid-file=./log/development.pid \
        --log-file=./log/development.log \
                   ./development.ini \
        stop
    ;;
  restart-dev)
    ./run paster serve \
        --daemon \
        --pid-file=./log/development.pid \
        --log-file=./log/development.log \
                   ./development.ini \
        restart
    ;;
  run-dev)
    ./run paster serve --reload \
    ./development.ini 
    ;;
  *)
    echo $"Usage: $0 {start|stop|restart|run|start-dev|stop-dev|restart-dev|run-dev}"
    exit 1
esac

