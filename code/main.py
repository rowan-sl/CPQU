import sys
from processor import CPQUProcessor

with open(sys.argv[1], "r") as f:
    program = f.read()

computer = CPQUProcessor(program)

print(computer.mem.size())
print(computer.mem.mem)

computer.run_till_done()