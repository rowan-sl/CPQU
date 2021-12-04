import sys
from processor import CPQUProcessor

with open(sys.argv[1], "r") as f:
    program = f.read()

computer = CPQUProcessor()
computer.load_program(program)

print("Memory size:")
print(computer.mem.size())
print("\nmem dump:")
print(computer.mem.mem)
print("\nrunning program:\n\n-------program starts--------")
computer.run_till_done()