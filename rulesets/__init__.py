__all__ = ['bridges', 'opening_hours', 'entrances']

class Memoize:
  def __init__ (self, f):
    self.f = f
    self.mem = {}
  def __call__ (self, *args, **kwargs):
    
      if (repr(args), repr(kwargs)) in self.mem:
        return self.mem[repr(args), repr(kwargs)]
      else:
        tmp = self.f(*args, **kwargs)
        self.mem[repr(args), repr(kwargs)] = tmp
        return tmp
    
    
def replace_bunch(bunch, to, where):
  for z in bunch:
    where = where.replace(z, to)
  return where