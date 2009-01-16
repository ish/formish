export GITDIR=$HOME/git
cd $GITDIR/formish/formish/tests/testish/
case "$1" in
  start)
    ./run paster serve \
        --daemon \
        --pid-file=$GITDIR/formish/formish/tests/testish/log/live.pid \
        --log-file=$GITDIR/formish/formish/tests/testish/log/live.log \
                   $GITDIR/formish/formish/tests/testish/live.ini \
        start
    ;;
  stop)
    ./run paster serve \
        --daemon \
        --pid-file=$GITDIR/formish/formish/tests/testish/log/live.pid \
        --log-file=$GITDIR/formish/formish/tests/testish/log/live.log \
                   $GITDIR/formish/formish/tests/testish/live.ini \
        stop
    ;;
  restart)
    ./run paster serve \
        --daemon \
        --pid-file=$GITDIR/formish/formish/tests/testish/log/live.pid \
        --log-file=$GITDIR/formish/formish/tests/testish/log/live.log \
                   $GITDIR/formish/formish/tests/testish/live.ini \
        restart
    ;;
  start-dev)
    ./run paster serve \
        --daemon \
        --pid-file=$GITDIR/formish/formish/tests/testish/log/development.pid \
        --log-file=$GITDIR/formish/formish/tests/testish/log/development.log \
                   $GITDIR/formish/formish/tests/testish/development.ini \
        start
    ;;
  stop-dev)
    ./run paster serve \
        --daemon \
        --pid-file=$GITDIR/formish/formish/tests/testish/log/development.pid \
        --log-file=$GITDIR/formish/formish/tests/testish/log/development.log \
                   $GITDIR/formish/formish/tests/testish/development.ini \
        stop
    ;;
  restart-dev)
    ./run paster serve \
        --daemon \
        --pid-file=$GITDIR/formish/formish/tests/testish/log/development.pid \
        --log-file=$GITDIR/formish/formish/tests/testish/log/development.log \
                   $GITDIR/formish/formish/tests/testish/development.ini \
        restart
    ;;
  *)
    echo $"Usage: $0 {start|stop|restart|start-dev|stop-dev|restart-dev}"
    exit 1
esac

