

class ScriptParser:
    simulation = None

    def parseScript(script_file):
        with open(script_file, 'r') as f:
            lines = f.readlines()

        for line in lines:
            # decide what kind of statement we're looking at

            # if timestep, do that
            if line[0] == '^':
                # advance time step

            elif line[0] == '#':
                parseConceptChange(line)
            elif line[0] == '+':
                parsePolicyChange(line)
            else:
                parseDataActivityProbability(line)

            # assume script[charPos] == '\n'
            charPos += 1

    def parseConceptChange(line):
        name = '>'.split(line)
        simulation.addConceptSubType(name[0], name[1])



'''
^
#:D2>D3
D2:0.25,0.5
D1:0.9,0.05
+:D3,R1,cr
'''
