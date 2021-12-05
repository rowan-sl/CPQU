import sys
import time
from processor import CPQUProcessor

with open(sys.argv[1], "r") as f:
    program = f.read()

computer = CPQUProcessor(False)
computer.load_program(program)

print("Memory size:")
print(computer.mem.size())
print("\nmem dump:")
print(computer.mem.mem)
print("\nrunning program:\n\n-------program starts--------")
start = time.time()
computer.run_till_done()
end = time.time()
print(f"\nProgram took {end-start} seconds to finish")