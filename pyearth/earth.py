from _forward import ForwardPasser
from _pruning import PruningPasser
import numpy as np

class Earth(object):
    forward_pass_arg_names = set(['endspan','minspan','endspan_alpha','minspan_alpha',
                                  'max_terms','max_degree','thresh','penalty','check_every',
                                  'min_searh_points','xlabels'])
    pruning_pass_arg_names = set(['penalty'])
    
    def __init__(self, **kwargs):
        
        #Check for unknown arguments
        unknown_args = self._pull_unknown_args(**kwargs)
        if unknown_args:
            msg = 'Unknown arguments: '
            for i, k, v in enumerate(unknown_args.iteritems()):
                msg += k+': '+str(v)
                if i < len(unknown_args) - 1:
                    msg += ', '
                else:
                    msg += '.'
            raise ValueError(msg)
        
        #Process forward pass arguments
        self.forward_pass_args = self._pull_forward_args(**kwargs)
        
        #Process pruning pass arguments
        self.pruning_pass_args = self._pull_pruning_args(**kwargs)
    
    def _pull_forward_args(self, **kwargs):
        result = {}
        for name in self.forward_pass_arg_names:
            if name in kwargs:
                result[name] = kwargs[name]
        return result
    
    def _pull_pruning_args(self, **kwargs):
        result = {}
        for name in self.pruning_pass_arg_names:
            if name in kwargs:
                result[name] = kwargs[name]
        return result
    
    def _pull_unknown_args(self, **kwargs):
        result = {}
        known_args = self.forward_pass_arg_names | self.pruning_pass_arg_names
        for name in kwargs.iterkeys():
            if name not in known_args:
                result[name] = kwargs[name]
        return result
    
    def fit(self, X, y, **kwargs):
        self.forward_pass(X, y)
        self.pruning_pass(X, y)
        self.linear_fit(X, y)
    
    def forward_pass(self, X, y, **kwargs):
        self.forward_passer = ForwardPasser(X, y, **self.forward_pass_args)
        self.forward_passer.run()
        self.basis = self.forward_passer.get_basis()
    
    def pruning_pass(self, X, y, **kwargs):
        self.pruning_passer = PruningPasser(self.basis, X, y)
        self.pruning_passer.run()
    
    def forward_trace(self):
        return self.forward_passer.trace()
    
    def pruning_trace(self):
        return self.pruning_passer.trace()
    
    def trace(self):
        return EarthTrace(self.forward_trace(),self.pruning_trace())
    
    def linear_fit(self, X, y):
        B = self.transform(X)
        self.beta = np.linalg.lstsq(B,y)[0]
    
    def predict(self, X):
        B = self.transform(X)
        return np.dot(B,self.beta)
    
    def transform(self, X):
        B = np.empty(shape=(X.shape[0],self.basis.plen()))
        self.basis.transform(X,B)
        return B

    def __str__(self):
        result = 'Earth Model\n'+'-'*80+'\n'
        for i, bf in enumerate(self.basis.piter()):
            result += str(bf) + '\t\t\t' + str(self.beta[i]) + '\n'
        return result

class EarthTrace(object):
    def __init__(self, forward_trace, pruning_trace):
        self.forward_trace = forward_trace
        self.pruning_trace = pruning_trace
        
    def __str__(self):
        return str(self.forward_trace) + '\n' + str(self.pruning_trace)