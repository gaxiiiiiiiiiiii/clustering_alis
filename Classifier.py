import MeCab

def get_words(text):
    m = MeCab.Tagger()
    words = []
    parsed = m.parse(text)
    for row in parsed.split("\n"):
        if row == "EOS":
            break
        word,features = row.split("\t")
        feature = features.split(",")[0]
        if feature == "名詞":
            words.append(word)
    return list(set(words))

class classifier:
    def __init__(self,getfeatures,filename=None):
        self.fc = {}
        self.cc = {}
        self.getfeatures = getfeatures
    
    def incf(self,f,cat):
        self.fc.setdefault(f,{})
        self.fc[f].setdefault(cat,0)
        self.fc[f][cat] += 1
        
    def incc(self,cat):
        self.cc.setdefault(cat,0)
        self.cc[cat] += 1
    
    def fcount(self,f,cat):
        if f in self.fc and cat in self.fc[f]:
            return self.fc[f][cat]
        return 0.0
    
    def catcount(self,cat):
        if cat in self.cc:
            return float(self.cc[cat])
        return 0
    
    def totalcount(self):
        return sum(self.cc.values())
    
    def categories(self):
        return self.cc.keys()
    
    def train(self,item,cat):
        features = self.getfeatures(item)
        for f in features:
            self.incf(f,cat)
        self.incc(cat)
    
    def fprob(self,f,cat):
        if self.catcount(cat) == 0:
            return 0
        
        return self.fcount(f,cat) / self.catcount(cat)
    
    def weightedprob(self,f,cat,prf,weight=1.0,ap=0.5):
        basicprob = prf(f,cat)
        totals = sum([self.fcount(f,c) for c in self.categories()])
        bp = ((weight*ap) + (totals*basicprob)) / (weight+totals)
        return bp

class naivebayes(classifier):
    def __init__(self,getfeatures=get_words):
        classifier.__init__(self,getfeatures)
        self.thresholds = {}
    
    def docprob(self,item,cat):
        features = self.getfeatures(item)
        
        p = 1
        for f in features:
            p *= self.weightedprob(f,cat,self.fprob)
        return p
        
    def setthreshold(self,cat,t):
        self.thresholds[cat] = t
    
    def getthreshold(self,cat):
        if cat not in self.thresholds:
            return 1.0
        return self.thresholds[cat]
    
    def prob(self,item,cat):
        catprob = self.catcount(cat)/self.totalcount()
        docprob = self.docprob(item,cat)
        return docprob*catprob
    
    def classify(self,item,default=None):
        probs = {}
        max = 0.0
        best = default
        for cat in self.categories():
            probs[cat] = self.prob(item,cat)
            if probs[cat] > max:
                max = probs[cat]
                best = cat
            
        for cat in probs:
            if cat == best:
                continue
            if probs[cat] * self.getthreshold(best) > probs[best]:
                return default
        return best