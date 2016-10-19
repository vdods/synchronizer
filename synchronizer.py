#!/usr/bin/python

import BaseHTTPServer
import locked_object
import math
import options
import requests
import sys
import threading
import time

g_options = None
g_exit_condition_semaphore = None
g_return_code = locked_object.LockedObject(None)

def log_verbose_message (message, *args):
    if g_options.verbose:
        sys.stdout.write(message.format(*args))
        sys.stdout.write('\n')

def debug_spew (message, *args):
    global g_options
    if g_options.debug_spew_enabled:
        sys.stdout.write(threading.current_thread().name)
        sys.stdout.write(': ')
        sys.stdout.write(message.format(*args))
        sys.stdout.write('\n')

def run_in_tell_mode ():
    global g_options
    global g_exit_condition_semaphore
    global g_return_code

    with g_exit_condition_semaphore:
        log_verbose_message('Running in `tell` mode.')
        debug_spew('Running in `tell` mode.')

        try:
            while len(g_options.tell_v) > 0:
                for tell_index,tell in enumerate(g_options.tell_v):
                    post_url = 'http://{0}'.format(tell.url)
                    post_data = tell.token
                    debug_spew('HTTP POST to {0} with data {1}', post_url, post_data)
                    try:
                        response = requests.post(post_url, data=post_data)
                        debug_spew('HTTP POST response status is {0}, text follows: {1}', response.status_code, response.text)
                        expected_response_text = 'INTERCOURSE the {0}!'.format(tell.token)
                        # If the HTTP POST was successful, cross off this tell element as completed.
                        if response.status_code == 200 and response.text == expected_response_text:
                            log_verbose_message('Successfully sent token {0} to {1}; {2} tokens left.', tell.token, post_url, len(g_options.tell_v)-1)
                            debug_spew('Successfully sent token {0} to {1} (out of {2} tell tokens).', tell.token, post_url, len(g_options.tell_v))
                            g_options.tell_v[tell_index] = None
                    except requests.exceptions.ConnectionError as e:
                        # This is fine, the `wait-for` service just isn't up yet.
                        debug_spew('The wait-for service at {0} is not up yet.', post_url)
                # Filter out the completed tell elements.
                g_options.tell_v = filter(lambda tell:tell is not None, g_options.tell_v)
                # Sleep if we're not done.
                if len(g_options.tell_v) > 0:
                    debug_spew('Sleeping for {0} seconds (set by --tell-period); {1} remaining tell tokens', g_options.tell_period, len(g_options.tell_v))
                    time.sleep(g_options.tell_period)

            with g_return_code as rc:
                log_verbose_message('All tokens successfully sent.')
                debug_spew('All tell tokens successfully sent; shutting down.')
                rc.value = 0
        except Exception as e:
            with g_return_code as rc:
                log_verbose_message('Error encountered: {0}', e)
                debug_spew('Error encountered in `tell` mode; shutting down; error was {0}', e)
                rc.value = -1

        debug_spew('About to release exit condition semaphore.')

class WaitFor (BaseHTTPServer.BaseHTTPRequestHandler):
    def do_POST (self):
        global g_options

        content_length = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_length)
        client_url = '{0}:{1}'.format(self.client_address[0], self.client_address[1])
        debug_spew('Received request body {0} from ', post_body, client_url)

        try:
            index = g_options.wait_for_v.index(post_body)
            log_verbose_message('Received expected token {0}; {1} tokens left.'.format(post_body, len(g_options.wait_for_v)-1))
            debug_spew('Token {0} successfully matched (out of {1} wait-for tokens).'.format(post_body, len(g_options.wait_for_v)))

            self.send_response(200) # OK (see https://en.wikipedia.org/wiki/List_of_HTTP_status_codes)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write('INTERCOURSE the ')
            self.wfile.write(post_body)
            self.wfile.write('!')

            g_options.wait_for_v[index] = None
            g_options.wait_for_v = filter(lambda wait_for:wait_for is not None, g_options.wait_for_v)
        except ValueError:
            log_verbose_message('Received unexpected token {0} from {1}', post_body, client_url)
            debug_spew('Token {0} from {1} did not match any wait-for token', post_body, client_url)
            self.send_response(400) # Bad Request (see https://en.wikipedia.org/wiki/List_of_HTTP_status_codes)

    def log_message(self, format, *args):
        """This override disables logging."""
        return

def run_in_wait_for_mode ():
    global g_options
    global g_exit_condition_semaphore
    global g_return_code

    with g_exit_condition_semaphore:
        server_address_and_port = ('localhost',g_options.wait_on_port)
        server_url = '{0}:{1}'.format(*server_address_and_port)
        log_verbose_message('Running in `wait-for` mode on {0}.', server_url)
        debug_spew('Running in `wait-for` mode on {0}.', server_url)

        httpd = BaseHTTPServer.HTTPServer(server_address_and_port, WaitFor)
        try:
            while len(g_options.wait_for_v) > 0:
                httpd.handle_request()
            with g_return_code as rc:
                log_verbose_message('All expected tokens received.')
                debug_spew('All expected wait-for tokens received; shutting down.')
                rc.value = 0
        except Exception as e:
            with g_return_code as rc:
                log_verbose_message('Error encountered: {0}', e)
                debug_spew('Error encountered in `wait-for` mode; shutting down; error was {0}', e)
                rc.value = -1
        finally:
            httpd.server_close()

        debug_spew('About to release exit condition semaphore.')

def run_timeout_waiter ():
    global g_options
    global g_exit_condition_semaphore
    global g_return_code

    with g_exit_condition_semaphore:
        debug_spew('Starting up; timeout is {0} seconds.', g_options.timeout)
        time.sleep(g_options.timeout)

        with g_return_code as rc:
            log_verbose_message('Timeout occurred (timeout was {0} seconds).', g_options.timeout)
            debug_spew('Timeout occurred (timeout was {0} seconds).', g_options.timeout)
            rc.value = -1

        debug_spew('About to release exit condition semaphore.')

def run_daemon_thread (target=None, name=None, args=(), kwargs={}):
    t = threading.Thread(target=target, name=name, args=args, kwargs=kwargs)
    # A daemon thread is such that if all non-daemon threads are dead, the program exits.
    t.daemon = True
    t.start()

def run_main_thread ():
    global g_exit_condition_semaphore
    global g_return_code

    try:
        # Hacky way to wait for the thread(s) to acquire g_exit_condition_semaphore.  This depends on
        # the threads successfully starting up within 1 second, which may not always be true.
        debug_spew('Waiting for daemon thread(s) to start.')
        time.sleep(1.0)
        debug_spew('Waiting on exit condition semaphore.')
        while True:
            acquired = g_exit_condition_semaphore.acquire(False) # Don't block
            if acquired:
                debug_spew('Acquired exit condition semaphore; waiting on return code lock.')
                with g_return_code as rc:
                    debug_spew('Acquired return code lock; program terminating with return code {0}.', rc.value)
                    sys.exit(rc.value)
            else:
                # Hacky way to keep the main thread available to listen for KeyboardInterrupt
                time.sleep(1.0)
    except KeyboardInterrupt:
        log_verbose_message('Caught KeyboardInterrupt; program terminating with return code {0}', -1)
        debug_spew('Caught KeyboardInterrupt; program terminating with return code {0}', -1)
        sys.exit(-1)

if __name__ == '__main__':
    g_options = options.Options(sys.argv[1:])

    if g_options.help_was_requested:
        sys.stdout.write(options.Options.help_message(sys.argv[0]))
        sys.exit(0)

    if not g_options.in_tell_mode and not g_options.in_wait_for_mode:
        log_verbose_message('No `tell` or `wait-for` requests made.')
        debug_spew('No `tell` or `wait-for` requests made; exiting with trivial success.')
        sys.exit(0)

    if g_options.in_tell_mode and g_options.in_wait_for_mode:
        sys.stderr.write('Must operate exclusively in `tell` mode or `wait-for` mode, not both.')
        sys.exit(-1)

    # Here on down is where the thread-based services start.

    if not math.isinf(g_options.timeout):
        # Give the semaphore a counter of 2; the timeout thread will acquire one count, while the tell/wait-for
        # thread will acquire the other, and the main thread will wait on whichever one quits first.
        g_exit_condition_semaphore = threading.Semaphore(2)
        run_daemon_thread(target=run_timeout_waiter, name='timeout thread')
    else:
        # Give the semaphore a counter of 1; there will only be one thread determining the exit condition
        # (the tell or wait-for thread).
        g_exit_condition_semaphore = threading.Semaphore(1)

    if g_options.in_tell_mode:
        run_daemon_thread(target=run_in_tell_mode, name='`tell` mode thread')
    else:
        assert g_options.in_wait_for_mode
        run_daemon_thread(target=run_in_wait_for_mode, name='`wait-for` mode thread')

    run_main_thread()
