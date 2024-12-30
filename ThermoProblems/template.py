# Author: Cameron F. Abrams, <cfa22@drexel.edu>
class Template:
    def __init__(self,templatefile='',keydelim=(r'<%',r'%>'),**kwargs):
        self.template=None
        if templatefile:
            with open(templatefile,'r') as f:
                self.template=f.read()
        ldelim_idx=[]
        rdelim_idx=[]
        self.ldelim,self.rdelim=keydelim
        for i,c in enumerate(self.template):
            if self.template[i:i+2]==self.ldelim:
                ldelim_idx.append(i)
            if self.template[i:i+2]==self.rdelim:
                rdelim_idx.append(i)
        keys=[]
        for l,r in zip(ldelim_idx,rdelim_idx):
            keys.append(self.template[l+2:r])
        self.keys=list(set(keys))
    def substitute_keys(self,map):
        template_local=self.template[:] # copy!
        for k in self.keys:
            tmp=template_local.replace(self.ldelim+k+self.rdelim,str(map[k]))
            template_local=tmp
        return template_local