from ajax_select import register, LookupChannel
from .models import Person
from django.db.models import Q

@register('person')
class PersonLookup(LookupChannel):

    model = Person

    def get_query(self, q, request):
        return self.model.objects.filter(Q(surname__istartswith = q) | Q(firstName__istartswith = q)).distinct('institutionEmail')

    def format_item_display(self, item):
        return u"<span class='person'>%s %s&emsp;%s&emsp;&emsp;%s</span>" % (item.firstName, item.surname, item.institutionEmail, item.institution.name)

    def format_match(self, item):
        return u"<span class='person'>%s %s&emsp;%s&emsp;%s</span>" % (item.firstName, item.surname, item.institutionEmail, item.institution.name)

@register('principalInvestigator')
class piLookup(LookupChannel):

    model = Person

    def get_query(self, q, request):
        return self.model.objects.filter(Q(surname__istartswith = q) | Q(firstName__istartswith = q)).distinct('institutionEmail')

    def format_item_display(self, item):
        return u"<span class='person'>%s %s&emsp;%s&emsp;%s</span>" % (item.firstName, item.surname, item.institutionEmail, item.institution.name)

    def format_match(self, item):
         return u"<span class='person'>%s %s&emsp;%s&emsp;%s</span>" % (item.firstName, item.surname, item.institutionEmail, item.institution.name)
