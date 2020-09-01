#!env/bin/python3

import sys, argparse
from consent_model import ConsentModel

def simulate(script, model):
    consent_history = {}
    lines = open(script, 'r').readlines()
    log = open('simulation.log', 'w')
    stderr = sys.stderr
    sys.stderr = log
    for line in lines:
        # skip empty lines
        if line.strip() == '':
            continue

        # process each command with trailing arguments
        command = line.split()

        if command[0] == 'step':
            time = model.step()
            
        elif command[0] == 'grant':
            retro = False
            if command[1] == 'retro':
                retro = True
                args = command[2:]
            else:
                args = command[1:]
            data = model.createData(args[0])
            ds = model.createDataSubject(args[1])
            recipient = model.createRecipient(args[2])
            consent = model.grantConsent(
                data, ds, recipient, retroactive=retro)
            consent_history[args[3]] = consent

        elif command[0] == 'withdraw':
            retro = False
            if command[1] == 'retro':
                retro = True
                args = command[2:]
            else:
                args = command[1:]
            consent = consent_history[args[0]]
            model.withdrawConsent(consent, retroactive=retro)
            
        elif command[0] == 'collect':
            args = command[1:]
            data = model.createData(args[0])
            ds = model.createDataSubject(args[1])
            recipient = model.createRecipient(args[2])
            model.collect(data, ds, recipient)
            
        elif command[0] == 'access':
            args = command[1:]
            data = model.createData(args[0])
            ds = model.createDataSubject(args[1])
            recipient = model.createRecipient(args[2])
            model.access(data, ds, recipient)

        elif command[0] == 'test':
            args = command[1:]
            data = model.createData(args[1])
            ds = model.createDataSubject(args[2])
            recipient = model.createRecipient(args[3])

            # run query for action type
            if args[0] == 'collect':
                result = model.isCollectable(data, ds, recipient)
            elif args[0] == 'access':
                result = model.isAccessible(data, ds, recipient)

            # report query result
            if args[4] == 'true' and result:
                print('PASS: %s (%s)' % (' '.join(args[0:-1]), args[-1]))
            elif args[4] == 'false' and not result:
                print('PASS: %s (%s)' % (' '.join(args[0:-1]), args[-1]))
            else:
                print('FAIL: %s (expected: %s, found: %s)' % (
                    ' '.join(args[0:-1]), args[-1], str(result).lower()))
        else:
            print('Unrecognized command: %s' % line)
            
    log.close()
    sys.stderr = stderr
    return
            
def main(argv):
    parser = argparse.ArgumentParser(
        description='Simulate consent model events')
    parser.add_argument('base_model', type=str,
                        help='the OWL file containing the base model')
    parser.add_argument('script', type=str,
                        help='the simulation script describing a scenario')
    parser.add_argument('ext_model', type=str, nargs='?',
                        help='the OWL file to save the simulation results')
    args = parser.parse_args()
    model = ConsentModel.load(args.base_model)
    simulate(args.script, model)
    if args.ext_model:
        model.save(args.ext_model)
    
if __name__ == "__main__":
    main(sys.argv[1:])
