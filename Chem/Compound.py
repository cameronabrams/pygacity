class Compound:
    ''' simple class for describing chemical compounds by empirical formula 
    
        e.g., 

        my_compound = Compound('A2B')

        creates a Compound instance my_compound for which my_compound.A is the
        following dictionary

        {'A':2, 'B':1}

        Empirical formulas can have nested parentheses, integer subscripts (1-implied if missing), and charges (indicated by a terminal '^{#}', where # is a string
        interpretable as a signed integer).  Element names can be either a single capital letter or a capital-lowercase dyad.  Another example:

        another_compound = Compound('H(OCH3CH2)10H')

        gives for another_compound.A:

        {'H':52, 'O':10, 'C':20}

        By parsing empirical formulas into element:count dictionaries, Compounds
        can be incorporated into Reactions and those Reactions can be balanced. 

        Cameron F. Abrams cfa22@drexel.edu 

    '''
    def __init__(self,ef,nameStr=''):
        if len(ef)>0:
            self.name=nameStr # optional namestring
            efc=ef.split('^')
            self.ef=efc[0]
            self.charge=0
            if len(efc)>1:
                expo=efc[1]
                if expo[0]=='{' and expo[-1]=='}':
                    self.charge=int(expo[1:-1])
                else:
                    print('Error: malformed charge:',efc[1])
            ''' dictionary of atomname:count items representing empirical formula '''
            self.A=parse_empirical_formula(self.ef)
            ''' To do: allow for charges in ef (as block superscripts) '''
            self.atomset=set(self.A.keys())
    def __str__(self):
        return self.ef+('' if self.charge==0 else r'^{'+f'{self.charge:+}'+r'}')
    def countAtoms(self,a):
        if a in self.A:
            return self.A[a]
        else:
            return 0

# per https://stackoverflow.com/users/5079316/olivier-melan%c3%a7on
def _push(obj,l,depth):
    while depth:
        l = l[-1]
        depth -= 1
    l.append(obj)

def _parse_parentheses(s):
    ''' byte-wise de-nestify a string with parenthesis '''
    groups = []
    depth = 0
    try:
        i=0
        while i<len(s):
#        for char in s:
            char=s[i]
            if char == '(':
                _push([], groups, depth)
                depth += 1
            elif char == ')':
                depth -= 1
            else:
                _push(char, groups, depth)
            i+=1
    except IndexError:
        raise ValueError('Parentheses mismatch')
    if depth != 0:
        raise ValueError('Parentheses mismatch')
    else:
        return groups

def bankblock(B,b):
    if len(b[0])>0: # bank this block
        if not any(isinstance(i, list) for i in b[0]):
            b[0]=''.join(b[0])
        nstr=''.join(b[1])
        b[1]=1 if len(nstr)==0 else int(nstr)
        B.append(b)

def blockify(bl):
    ''' parse the byte_levels returned from the byte-wise de-nester into blocks, where
        a block is a two-element list, where first element is a block and second is 
        an integer subscript >= 1.  A "primitive" block is one in which the first
        element is not a list, but instead a string that indentifies a chemical element. '''
    blocks=[]
    curr_block=[[],[]]
    for b in bl:
        if len(b)==1:
            if b.isalpha():
                if b.isupper(): # new block
                    bankblock(blocks,curr_block)
                    curr_block=[[b],[]]
                else: # still building this block's elem name
                    curr_block[0].append(b)
            elif b.isdigit():
                curr_block[1].append(b)
        else:
            bankblock(blocks,curr_block)
            curr_block=[blockify(b),[]]
    bankblock(blocks,curr_block)
    return blocks

def flattify(B):
    ''' distribute the block counts inward '''
    for b in B:
        if isinstance(b[0],str) or b[1]==1: # already flat
            pass
        else:
            m=b[1]
            b[1]=1
            for bb in b[0]:
                bb[1]*=m
                flattify(b[0])

def my_flatten(L,size=(2)):
    ''' flatten '''
    flatlist=[]
    for i in L:
        if not isinstance(i[0],list):
            flatlist.append(i)
        else:
            newlist=my_flatten(i[0])
            flatlist.extend(newlist)
    return flatlist

def reduce(L):
    ''' produce a dictionary of element:number '''
    result_dict={}
    for i in L:
        if i[0] in result_dict:
            result_dict[i[0]]+=i[1]
        else:
            result_dict[i[0]]=i[1]
    return result_dict

def parse_empirical_formula(ef):
    block_levels=blockify(_parse_parentheses(ef))
    flattify(block_levels)
    return reduce(my_flatten(block_levels))

if __name__ == '__main__':
    compounds=[]
    empirical_formulas={'methane':'CH4','methanol':'CH3OH','n-butane':'CH3(CH2)2CH3','water':'H2O','hydrogen':'H2','silver chloride':'AgCl','silver nitrate':'AgNO3','sodium chloride':'NaCl','sodium nitrate':'NaNO3','calcium nitrate':'Ca(NO3)2','sodium sulfate':'Na2SO4','cobalt chloride':'CoCl2','cobalt nitrate':'Co(NO3)2','phenol':'C6H5OH','toluene':'C6H5CH3','some polyether':'CH3(OCH2)10CH3','graphite':'C','hydroxide':'OH^{-1}'}
    for name,ef in empirical_formulas.items():
        compounds.append(Compound(ef,nameStr=name))
    for c in compounds:
        print(f'{str(c):>20s} = {c.A}')
    

