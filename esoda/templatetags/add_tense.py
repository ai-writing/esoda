from django import template

register = template.Library()

@register.filter
def add_tense(word):
    # TODO 
    return word
    # if word.endswith('e'):
    #     return word + 'd/ing'
    # else:
    #     return word + 'ed/ing'
