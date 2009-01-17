export GITDIR=$HOME/git
cd $GITDIR/formish/formish/tests/testish/
case "$1" in
  start)
    ./run /home/tim/py/bin/paster serve \
        --daemon \
        --pid-file=$GITDIR/formish/formish/tests/testish/log/live.pid \
        --log-file=$GITDIR/formish/formish/tests/testish/log/live.log \
                   $GITDIR/formish/formish/tests/testish/live.ini \
        start
    ;;
  stop)
    ./run /home/tim/py/bin/paster serve \
        --daemon \
        --pid-file=$GITDIR/formish/formish/tests/testish/log/live.pid \
        --log-file=$GITDIR/formish/formish/tests/testish/log/live.log \
                   $GITDIR/formish/formish/tests/testish/live.ini \
        stop
    ;;
  restart)
    ./run /home/tim/py/bin/paster serve \
        --daemon \
        --pid-file=$GITDIR/formish/formish/tests/testish/log/live.pid \
        --log-file=$GITDIR/formish/formish/tests/testish/log/live.log \
                   $GITDIR/formish/formish/tests/testish/live.ini \
        restart
    ;;
  run)
    ./run /home/tim/py/bin/paster serve \
        --log-file=$GITDIR/formish/formish/tests/testish/log/live.log \
                   $GITDIR/formish/formish/tests/testish/live.ini
    ;;
  start-dev)
    ./run /home/tim/py/bin/paster serve \
        --daemon \
        --pid-file=$GITDIR/formish/formish/tests/testish/log/development.pid \
        --log-file=$GITDIR/formish/formish/tests/testish/log/development.log \
                   $GITDIR/formish/formish/tests/testish/development.ini \
        start
    ;;
  stop-dev)
    ./run /home/tim/py/bin/paster serve \
        --daemon \
        --pid-file=$GITDIR/formish/formish/tests/testish/log/development.pid \
        --log-file=$GITDIR/formish/formish/tests/testish/log/development.log \
                   $GITDIR/formish/formish/tests/testish/development.ini \
        stop
    ;;
  restart-dev)
    ./run /home/tim/py/bin/paster serve \
        --daemon \
        --pid-file=$GITDIR/formish/formish/tests/testish/log/development.pid \
        --log-file=$GITDIR/formish/formish/tests/testish/log/development.log \
                   $GITDIR/formish/formish/tests/testish/development.ini \
        restart
    ;;
  run-dev)
    ./run /home/tim/py/bin/paster serve --reload \
                   $GITDIR/formish/formish/tests/testish/development.ini
    ;;
  *)
    echo $"Usage: $0 {start|stop|restart|run|start-dev|stop-dev|restart-dev|run-dev}"
    exit 1
esac

