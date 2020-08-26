#!env/bin/python3

import sys, argparse
from consent_model import ConsentModel

def simulate(script, model):
    consent_history = {}
    lines = open(script, 'r').readlines()
    for line in lines:
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
    if args.output:
        model.save(args.ext_model)
    
if __name__ == "__main__":
    main(sys.argv[1:])
