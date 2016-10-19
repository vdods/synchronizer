# synchronizer

A simple Python utility for synchronizing commandline processes, e.g. in docker-compose.

For now, it's implemented against Python 2.7, but may be ported to Python 3.x in the future.

# Notes and Todos

-	The --tell command should default to localhost and the default port (45954) if none is specified.
	The underlying principle being that the use case of a single tell'er and wait'er should be very terse,
	such as (noting that this usage doesn't exist yet)

		`python2 synchronizer.py --tell=SPLUNGE`

	In one process, and

		`python2 synchronizer.py --wait-for=SPLUNGE`

	in the other.  The next level up would be using localhost as the default address but specifying the port,
	where there may be multiple tell'ers and wait'ers, such as

		`python2 synhcronizer.py --wait-on-port=49000 --wait-for=SPLUNGE`

		`python2 synchronizer.py --wait-on-port=50000 --wait-for=GUMBY`

		`python2 synchronizer.py --tell=49000/SPLUNGE --tell=50000/GUMBY`
-	Add a lock to the output stream so output like this doesn't happen:

		`wait-for` mode threadMainThread: Waiting for daemon thread(s) to start.: Running in `wait-for` mode on localhost:45954.

		MainThread: Waiting on exit condition semaphore.
-	Maybe allow --tell and --wait-for at the same time.
