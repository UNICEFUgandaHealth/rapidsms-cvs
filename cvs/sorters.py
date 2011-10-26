from generic.sorters import Sorter
from rapidsms.models import Connection
from rapidsms_xforms.models import XFormSubmission, XFormSubmissionValue
from script.models import ScriptSession
from eav.models import Attribute

class LatestSubmissionSorter(Sorter):
    def sort(self, column, object_list, ascending=True):
        connections = list(Connection.objects.filter(contact__in=object_list))
        submissions = list(XFormSubmission.objects.filter(connection__in=connections).order_by('-created').select_related('connection__contact__healthproviderbase__facility', 'connection__contact__healthproviderbase__location'))
        full_contact_list = list(object_list)
        toret = []
        for sub in submissions:
            if not (sub.connection.contact.healthproviderbase in toret):
                toret.append(sub.connection.contact.healthproviderbase)
        nosubmissions = []
        for c in full_contact_list:
            if not (c in toret):
                nosubmissions.append(c)

        toret = toret + nosubmissions
        if not ascending:
            toret.reverse()
        return toret


class LatestJoinedSorter(Sorter):
    def sort(self, column, object_list, ascending=True):
        connections = list(Connection.objects.filter(contact__in=object_list))
        sessions = list(ScriptSession.objects.filter(script__slug='cvs_autoreg', connection__in=connections).order_by('-end_time').select_related('connection__contact__healthproviderbase__facility', 'connection__contact__healthproviderbase__location'))
        full_contact_list = list(object_list)
        toret = []
        for s in sessions:
            if not (s.connection.contact.healthproviderbase in toret):
                toret.append(s.connection.contact.healthproviderbase)
        nosessions = []
        for c in full_contact_list:
            if not (c in toret):
                nosessions.append(c)

        toret = toret + nosessions
        if not ascending:
            toret.reverse()
        return toret


class SubmissionValueSorter(Sorter):
    def sort(self, column, object_list, ascending=True):
        if len(object_list):
            submissions = list(object_list)
            xform = submissions[0].xform
            a = Attribute.objects.get(slug=column)
            if a.datatype == Attribute.TYPE_TEXT:
                order_by = 'value_text'
            elif a.datatype == Attribute.TYPE_INT:
                order_by = 'value_int'
            elif a.datatype == Attribute.TYPE_DATE:
                order_by = 'value_date'
            elif a.datatype == Attribute.TYPE_BOOLEAN:
                order_by = 'value_bool'
            elif a.datatype == Attribute.TYPE_OBJECT:
                order_by = 'generic_value_id'
            if order_by:
                values = list(XFormSubmissionValue.objects.filter(attribute__slug=column).order_by(order_by))
                toret = []
                for v in values:
                    if not v.submission in toret:
                        toret.append(v.submission)
                for s in submissions:
                    if not s in toret:
                        toret.append(s)
                if not ascending:
                    toret.reverse()
                return toret
        return object_list
