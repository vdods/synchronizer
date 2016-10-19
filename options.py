import getopt
import sys

class TellSpec:
    def __init__ (self, tell_spec_string):
        try:
            self.url,self.token = tell_spec_string.split('/', 2)
        except ValueError as e:
            sys.stderr.write('Invalid `tell` option; expected the form address:port/token\n')
            sys.exit(2)

    def tell (self):
        pass

class Options:
    def __init__ (self, argv):
        opt_v,arg_v = getopt.getopt(
            argv,
            '',
            [
                'help',
                'tell=',
                'tell-period=',
                'timeout=',
                'wait-for=',
                'wait-on-address=',
                'wait-on-port=',
                'verbose=',
                'debug-spew=',
                'output-stream=',
            ]
        )

        self.help_was_requested = False
        self.tell_v             = []
        self.tell_period        = 1.0
        self.timeout            = float('inf')
        self.wait_for_v         = []
        self.wait_on_address    = 'localhost'
        self.wait_on_port       = 45954
        self.verbose            = False
        self.debug_spew_enabled = False
        self.output_stream      = sys.stdout

        for opt in opt_v:
            if opt[0] == '--help':
                self.help_was_requested = True
            elif opt[0] == '--tell':
                self.tell_v.append(TellSpec(opt[1]))
            elif opt[0] == '--tell-period':
                self.tell_period = float(opt[1])
            elif opt[0] == '--timeout':
                self.timeout = float(opt[1])
                assert self.timeout >= 0.0, 'timeout must be non-negative (can be inf)'
            elif opt[0] == '--wait-for':
                self.wait_for_v.append(opt[1])
            elif opt[0] == '--wait-on-address':
                self.wait_on_address = opt[1]
            elif opt[0] == '--wait-on-port':
                self.wait_on_port = int(opt[1])
            elif opt[0] == '--verbose':
                self.verbose = opt[1].lower() in ['true', 'yes', 'on', '1']
            elif opt[0] == '--debug-spew':
                self.debug_spew_enabled = opt[1].lower() in ['true', 'yes', 'on', '1']
            elif opt[0] == '--output-stream':
                if opt[1].lower() not in ['stdout', 'stderr']:
                    sys.stderr.write('Argument to --output-stream must be one of stdout or stderr (case insensitive).\n')
                    sys.exit(2)
                self.output_stream = sys.stdout if opt[1].lower() == 'stdout' else sys.stderr
            else:
                sys.stderr.write('Invalid option: {0}\n'.format(opt))
                sys.exit(2)

        self.in_tell_mode = len(self.tell_v) > 0
        self.in_wait_for_mode = len(self.wait_for_v) > 0

    @staticmethod
    def help_message (program_name):
        return (
            'Usage: {0} [options]\n'
            '\n'
            '    Utility to perform simple `wait for X to happen` style synchronization via commandline.  Operates either\n'
            '    in `tell` mode or `wait-for` mode.  The `tell` mode consists of attempting to HTTP POST a particular token\n'
            '    to each of specified target hosts before exiting with success.  The `wait` mode consists of waiting to\n'
            '    receive particular tokens via HTTP POST requests before exiting with success.  If the stopping condition\n'
            '    is not met before the timeout condition is met, then the program exits with error.\n'
            '\n'
            'Options:\n'
            '           --help       : Print this help message and then exits with return code 0.\n'
            '           --tell=<arg> : If <arg> has the form address:port/token, then periodically attempts to HTTP POST\n'
            '                          token to address:port.  Stops upon success.  Program exits with return code 0 if\n'
            '                          every `tell` succeeded, otherwise exits with return code 1 if the timeout condition\n'
            '                          was reached.\n'
            '    --tell-period=<arg> : The number of seconds between attempts to `tell`.  Can be decimal-valued.  Default\n'
            '                          is 1.0.\n'
            '        --timeout=<arg> : The number of seconds before the program exits with return code 1 if it hasn\'t\n'
            '                          succeded.  Can be decimal-valued.  Default is inf (i.e. no timeout).\n'
            '       --wait-for=<arg> : Waits for the token <arg> to be HTTP POST\'ed on given port.  Multiple such waits\n'
            '                          can be made, even with duplicate token values.  Program exits with return code 0\n'
            '                          if each wait request was successfully received, otherwise exits with return code 1\n'
            '                          if the timeout condition was reached.\n'
            '--wait-on-address=<arg> : Specifies which address the `wait-for` server will be offered on.  Default value\n'
            '                          is localhost.\n'
            '   --wait-on-port=<arg> : Defines the port on which `wait` requests will be received.  Default value is 45954.\n'
            '        --verbose=<arg> : Enables verbose mode, which will cause certain operational messages to be printed.\n'
            '                          An <arg> value of true, yes, on, or 1 (case insensitive) will enable this, while\n'
            '                          anything else disables it.\n'
            '     --debug-spew=<arg> : Enables messages used for debugging.  The <arg> value is parsed as in --verbose.\n'
            '  --output-stream=<arg> : An <arg> value of stdout or stderr specifies which file stream all debug-spew and\n'
            '                          verbose messaging should be sent to.\n'.format(program_name)
        )

