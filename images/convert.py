from collections import Counter

with open('seen.csv') as fp, open('favourite.csv') as fp2, open('color.csv', 'w') as op1:
   seen = Counter([line for line in fp])
   seen = [key for key in seen if seen[key] % 2 == 1]
   favourite = Counter([line for line in fp2])
   favourite = [key for key in favourite if (favourite[key] % 2) == 1]
   for key in favourite:
       op1.write('%s BurlyWood\n' % key.strip())
