from formish.dottedDict import dottedDict

d = {'one': {'a': 3, 'b':9, 'c': {'x':3, 'y':5}}}
D = dottedDict(d)
import wingdbstub
print D.dotteditems()
print D.data
