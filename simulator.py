#!env/bin/python3

import sys, argparse
from consent_model import ConsentModel

def simulate(script, model, logging=True):
    # redirect standard error to the simulation log
    if logging:
        log = open('simulation.log', 'w')
        stderr = sys.stderr
        sys.stderr = log

    # setup table to lookup consent reference names
    consent_history = {}

    # read and process lines in script
    lines = open(script, 'r').readlines()
    for line in lines:
        # skip empty lines
        if line.strip() == '':
            continue
        elif line[0] == '#':
            continue

        # process each command with trailing arguments
        command = line.split()

        if command[0] == 'step':
            # advance one time step
            time = model.step()

        elif command[0] == 'set':
            # toggle states in the model or simulator
            value = None
            if command[1] == 'destroy_queries':
                value = command[2] == 'true'
                model.destroy_queries = value

            print('set %s = %s' % (command[1], value))
            
        elif command[0] == 'grant':
            # check for optional retroactivity
            retro = False
            if command[1] == 'retro':
                retro = True
                args = command[2:]
            else:
                args = command[1:]

            # parse consent arguments, add consent to model and history
            data = model.createData(args[0])
            data_subject = model.createDataSubject(args[1])
            collect_recipient = model.createRecipient(args[2])
            consent = model.grantConsent(
                data, data_subject, collect_recipient, retroactive=retro)
            consent_history[args[3]] = consent

        elif command[0] == 'withdraw':
            # check for optional retroactivity
            retro = False
            if command[1] == 'retro':
                retro = True
                args = command[2:]
            else:
                args = command[1:]

            # lookup and withdraw consent
            consent = consent_history[args[0]]
            model.withdrawConsent(consent, retroactive=retro)
            
        elif command[0] == 'collect':
            # parse collection arguments, add collection to model
            args = command[1:]
            data = model.createData(args[0])
            data_subject = model.createDataSubject(args[1])
            recipient = model.createRecipient(args[2])
            model.collect(data, data_subject, recipient)
            
        elif command[0] == 'access':
            # parse access arguments, add access to model
            args = command[1:]
            data = model.createData(args[0])
            data_subject = model.createDataSubject(args[1])
            recipient = model.createRecipient(args[2])
            
            # check for optional time constraints
            collect_at = [None, None]
            if len(args) > 3:
                collect_at[0] = model.getTime(args[4])
            if len(args) > 4:
                collect_at[1] = model.getTime(args[5])

            model.access(data, data_subject, recipient, collect_at)

        elif command[0] == 'assume':
            args = command[1:]
            expected = args[0]
            action = args[1]
            data = model.createData(args[2])
            data_subject = model.createDataSubject(args[3])
            recipient = model.createRecipient(args[4])

            # check for optional time constraints
            collect_at = [None, None]
            if len(args) > 5:
                collect_at[0] = model.getTime(args[5])
            if len(args) > 6:
                collect_at[1] = model.getTime(args[6])
            access_at = [None, None]
            if len(args) > 7:
                access_at[0] = model.getTime(args[7])
            if len(args) > 8:
                access_at[1] = model.getTime(args[8])
                
            # run query for action type
            if action == 'collect':
                index, result = model.isCollectable(
                    data, data_subject, recipient, collect_at)
            elif action == 'access':
                index, result = model.isAccessible(
                    data, data_subject, recipient, collect_at, access_at)

            # report query result
            if expected == 'true' and result:
                print('%s PASS: %s (%s)' % (
                    index, ' '.join(args[1:]), args[0]))
            elif expected == 'false' and not result:
                print('%s PASS: %s (%s)' % (
                    index, ' '.join(args[1:]), args[0]))
            else:
                print('%s FAIL: %s (expected: %s, found: %s)' % (
                    index, ' '.join(args[1:]), args[0], str(result).lower()))

        # create new data and recipient classes
        elif command[0] == 'new':
            args = command[2:]
            if command[1] == 'data':
                if len(args) == 1:
                    args.append('Data')
                model.createData(args[0], args[1])
            elif command[1] == 'recipient':
                model.createRecipient(args[0])
                
        else:
            print('Unrecognized command: %s' % line)

    # return standard error to original configuration
    if logging:
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
    parser.add_argument('--nologging', action='store_true',
                        help='log standard error to simulation.log')
    args = parser.parse_args()
    model = ConsentModel.load(args.base_model)
    simulate(args.script, model, logging = args.nologging == False)
    if args.ext_model:
        model.save(args.ext_model)
    
if __name__ == "__main__":
    main(sys.argv[1:])
