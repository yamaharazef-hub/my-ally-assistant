import nltk
from nltk.corpus import wordnet
from plugin import plugin

nltk.data.path.append("allycli/data/ntlk")


@plugin('dictionary')
def dictionary(ally, s):
    """
    Get meaning, synonym and antonym of any word
    """
    if len(s) == 0:
        ally.say('\nEnter word')
        word = ally.input()
    else:
        word = s

    syns = wordnet.synsets(word)
    if len(syns) == 0:
        ally.say("Don't recognise that word")
        return

    synonyms, antonyms = build_datasets(ally, word, syns)

    ally.say('\nSynonyms:\n' + ", ".join(synonyms))
    ally.say('\nAntonyms:\n' + ", ".join(antonyms))

    # detail loop
    def input_detail_id():
        ally.say("")
        synlen = len(syns)
        detail_id = ally.input("Details of meaning (1-{}): ? ".format(synlen))
        if detail_id == '':
            return None

        try:
            detail_id = int(detail_id)
        except ValueError:
            return input_detail_id()

        if detail_id <= 0 or detail_id > synlen:
            ally.say("Choose Value between 1 and {}".format(synlen))
            return input_detail_id()

        return detail_id

    detail_id = input_detail_id()
    while detail_id is not None:
        meaning = syns[detail_id - 1]

        synonyms = [synonym for synonym in meaning.lemma_names()
                    if synonym != word]
        examples = meaning.examples()

        antonyms = set()
        for synonym in meaning.lemmas():
            for antonym in synonym.antonyms():
                antonyms.add(antonym.name())

        present_results(ally, synonyms, antonyms, detail_id, meaning, examples)

        detail_id = input_detail_id()

def present_results(ally, synonyms, antonyms, detail_id, meaning, examples):
    ally.say('')
    ally.say('== {}. =='.format(detail_id))
    ally.say("Meaning  : {}".format(meaning.definition()))
    if len(synonyms) > 0:
        ally.say("Synonyms : {}".format(", ".join(synonyms)))
    if len(antonyms) > 0:
        ally.say("Antonyms : {}".format(", ".join(antonyms)))
    if len(examples) > 0:
        if len(examples) == 1:
            ally.say("Examples : {}".format(examples[0]))
        else:
            ally.say("Examples :\n-{}".format("\n- ".join(examples)))

def build_datasets(ally, word, syns):
    synonyms = set()
    antonyms = set()

    count = 0
    for meaning in syns:
        count = count + 1
        ally.say("{:>3}. {}".format(count, meaning.definition()))

        for synonym in meaning.lemmas():
            if synonym.name() != word:
                synonyms.add(synonym.name())
            for antonym in synonym.antonyms():
                antonyms.add(antonym.name())
    return synonyms,antonyms
