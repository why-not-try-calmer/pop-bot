import sys
import pstats

p = pstats.Stats(sys.argv[1])
p.strip_dirs()
p.sort_stats('cumtime')
p.print_stats(50)