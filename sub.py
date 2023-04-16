import spacy
import claucy 

sent_text = []
with open('data/tmp/sent_text.txt', 'r') as f:
    for line in f:
        sent_text.append(line.strip())
nlp = spacy.load('en_core_web_sm')

parsed_text = nlp(sent_text[2])

#get token dependencies
for text in parsed_text:
    #subject would be
    if text.dep_ == "nsubj":
        subject = text.orth_
        print(f"subject: {subject}")
    #iobj for indirect object
    if text.dep_ == "iobj":
        indirect_object = text.orth_
        print(f"indirect object: {indirect_object}")
    #dobj for direct object
    if text.dep_ == "dobj":
        direct_object = text.orth_
        print(f"direct object: {direct_object}")

# https://github.com/mmxgn/spacy-clausie
claucy.add_to_pipe(nlp)
doc = nlp(parsed_text)

doc._.clauses
propositions = doc._.clauses[0].to_propositions(as_text=True)
print(propositions)

import pdb
pdb.set_trace()

