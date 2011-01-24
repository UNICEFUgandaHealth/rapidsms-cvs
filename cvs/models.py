from rapidsms_xforms.models import XFormField, dl_distance, xform_received
import re
import datetime
from healthmodels.models import *
from healthmodels.models.HealthProvider import HealthProviderBase
from simple_locations.models import Point, Area, AreaType
from django.core.exceptions import ValidationError
from code_generator.code_generator import get_code_from_model, generate_tracking_tag, generate_code
from django.contrib.auth.models import Group

def parse_timedelta(command, value):
    lvalue = value.lower().strip()
    now = datetime.datetime.now()
    try:
        return (now -  datetime.datetime.strptime(lvalue, '%m-%d-%Y')).days
    except ValueError:
        try:
            return (now -  datetime.datetime.strptime(lvalue, '%m/%d/%Y')).days
        except ValueError:   
            rx = re.compile('[0-9]*')
            m = rx.match(lvalue)
            number = lvalue[m.start():m.end()].strip()
            unit = lvalue[m.end():].strip()
            if number:
                number = int(number)
                unit_dict = {
                    ('day','days','dys','ds','d'):1,
                    ('week', 'wk','wks','weeks','w'):7,
                    ('month', 'mo','months','mnths','mos','ms','mns','mnth','m'):30,
                    ('year', 'yr','yrs','y'):365,
                }
                for words, days in unit_dict.iteritems():
                    for word in words:
                        if dl_distance(word, unit) <= 1:
                            return days*number    
            
    raise ValidationError("Expected an age got: %s." % value)
    #do something to parse a time delta
    #raise ValidationError("unknown time length or something")

    #cleaned_value = like a timedelta or something
    #return cleaned_value

# register timedeltas as a type

def parse_place(command, value):
    lvalue = value.lower().strip()
    for w in ('clinic', 'facility', 'hc','hospital'):
        if dl_distance(lvalue, w) <= 1:
            return 'FACILITY'
    if dl_distance(lvalue, 'home') <= 1:
        return 'HOME'
    else:
        raise ValidationError("Did not understand the location: %s." % value)

def parse_gender(command, value):
    # return m or f
    lvalue = value.lower().strip()
    if (lvalue == 'm') or (dl_distance(lvalue, 'male') <= 1):
        return 'M'
    elif (lvalue == 'f') or (dl_distance(lvalue, 'female') <= 1):
        return 'F'
    else:
        raise ValidationError("Expected the patient's gender "
                    "(\"male\", \"female\", or simply \"m\" or \"f\"), "
                    "but received instead: %s." % value)

def parse_muacreading(command, value):
    lvalue = value.lower().strip()
    rx = re.compile('[0-9]*')
    m = rx.match(lvalue)
    reading = lvalue[m.start():m.end()]
    remaining = lvalue[m.end():].strip()
    try:
        reading = int(reading)
        if remaining == 'mm':
            if reading <= 30:
                reading *= 10
        elif remaining == 'cm':
            reading *= 10
        if reading > 125:
            return'G'
        elif reading < 114:
            return 'R'
        else:
            return 'Y'
    except ValueError:
        for category, word in (('R', 'red'), ('Y','yellow'), ('G','green')):
            if (lvalue == category.lower()) or (dl_distance(lvalue, word) <= 1):
                return category
    raise ValidationError("Expected a muac reading "
                "(\"green\", \"red\", \"yellow\" or a number), "
                "but received instead: %s." % value)
    

def parse_oedema(command, value):
    lvalue = value.lower().strip()
    if dl_distance(lvalue, 'oedema') <= 1:
        return 'T'
    else:
        return 'F'
    
def parse_facility(command, value):
    try:
        return HealthFacility.objects.get(code=value)
    except:
        raise ValidationError("Expected an HMIS facility code (got: %s)." % value)       

XFormField.register_field_type('cvssex', 'Gender', parse_gender,
                               db_type=XFormField.TYPE_TEXT, xforms_type='string')

XFormField.register_field_type('cvsloc', 'Place', parse_place,
                               db_type=XFormField.TYPE_TEXT, xforms_type='string')

XFormField.register_field_type('cvstdelt', 'Time Delta', parse_timedelta,
                               db_type=XFormField.TYPE_INT, xforms_type='integer')

XFormField.register_field_type('cvsmuacr', 'Muac Reading', parse_muacreading,
                               db_type=XFormField.TYPE_TEXT, xforms_type='string')

XFormField.register_field_type('cvsodema', 'Oedema Occurrence', parse_oedema,
                               db_type=XFormField.TYPE_TEXT, xforms_type='string')

XFormField.register_field_type('facility', 'Facility Code', parse_facility,
                               db_type=XFormField.TYPE_OBJECT, xforms_type='string')

def get_or_create_patient(health_provider, patient_name, birthdate=None, deathdate=None, gender=None):
    return create_patient(health_provider, patient_name, birthdate, deathdate, gender)

def create_patient(health_provider, patient_name, birthdate, deathdate, gender):
    names = patient_name.split(' ')
    first_name = names[0]
    last_name = ''
    middle_name = ''
    if len(names) > 1:
        last_name = names[len(names) - 1]
    if len(names) > 2:
        middle_name = ' '.join(names[1:-1])

    healthcode = generate_tracking_tag()
    if HealthId.objects.count():
        healthcode = HealthId.objects.order_by('-pk')[0].health_id
        healthcode = generate_tracking_tag(healthcode)
    healthid = HealthId.objects.create(
        health_id = healthcode
    )
    healthid.save()
    patient = Patient.objects.create(
         health_id=healthid,
         first_name=first_name,
         middle_name=middle_name,
         last_name=last_name,
         gender=gender,
         birthdate=birthdate,
         deathdate=deathdate,
    )
    patient.save()
    healthid.issued_to = patient
    healthid.save()
    patient.health_worker=health_provider
    patient.save()
    return patient

def check_validity(xform_type, health_provider, patient=None):
    return True

def patient_label(patient):
        gender = 'male' if patient.gender == 'M' else 'female'

        days = patient.age.days
        if days > 365:
            age_string = "aged %d" % (days // 365)
        elif days > 30:
            age_string = "(%d months old)" % (days // 30)
        else:
            age_string = "(infant)"

        return "%s, %s %s" % (patient.full_name(), gender, age_string)

def xform_received_handler(sender, **kwargs):
    
    disease_dict = {
        'bd':'Bloody diarrhea (Dysentery)',
        'ma':'Malaria',
        'tb':'Tuberculosis',
        'ab':'Animal Bites',
        'af':'Acute Flaccid Paralysis (Polio)',
        'mg':'Meningitis',
        'me':'Measles',
        'ch':'Cholera',
        'gw':'Guinea Worm',
        'nt':'Neonatal Tetanus',
        'yf':'Yellow Fever',
        'pl':'Plague',
        'ra':'Rabies',   
        'vf':'Other Viral Hemorrhagic Fevers',
        'ei':'Other Emerging Infectious Diseases',
    }

    home_dict = {
        'it':'ITTNs/LLINs',
        'la':'Latrines',
        'ha':'Handwashing Facilities',
        'wa':'Safe Drinking Water',            
    }

    xform = kwargs['xform']
    submission = kwargs['submission']

    # TODO: check validity
    patient = None
    kwargs.setdefault('message', None)
    message = kwargs['message']
    if not message:
        return
    if xform.keyword == 'reg':
        if submission.connection.contact:
            hp = HealthProvider.objects.create(pk=submission.connection.contact.pk)
        else:
            hp = HealthProvider.objects.create()
        hp.name = submission.eav.reg_name
        hp.save()
        return

    try:
        health_provider = submission.connection.contact.healthproviderbase.healthprovider
    except HealthProviderBase.DoesNotExist:
        submission.response = "Must be a reporter. Please register first with your name."
        submission.save()
        return
    if xform.keyword == 'pvht':
        health_provider.groups.add(Group.objects.get(name='Peer Village Health Team'))
        health_provider.facility = submission.eav.pvht_facility
        health_provider.save()        
        return
    if xform.keyword == 'vht':
        health_provider.groups.add(Group.objects.get(name='Village Health Team'))
        health_provider.facility = submission.eav.vht_facility
        health_provider.save()
        return
    if xform.keyword == 'muac':
        days = submission.eav.muac_age
        birthdate = datetime.date.today() - datetime.timedelta(days=days)
        patient = get_or_create_patient(health_provider, submission.eav.muac_name, birthdate=birthdate, gender=submission.eav.muac_gender)
        valid = check_validity(xform.keyword, health_provider, patient)
        report = PatientEncounter.objects.create(
                submission=submission,
                reporter=health_provider,
                patient=patient,
                message=message,
                valid=valid)
        muac_label = "Severe Acute Malnutrition" if (submission.eav.muac_category == 'R') else "Risk of Malnutrition"
        submission.response = "%s has been identified with %s" % (patient_label(patient), muac_label)
        submission.save()
        return
    elif xform.keyword == 'birth':
        patient = create_patient(health_provider, submission.eav.birth_name, birthdate=datetime.datetime.now(), gender=submission.eav.birth_gender)
        valid = check_validity(xform.keyword, health_provider, patient)
        report = PatientEncounter.objects.create(
                submission=submission,
                reporter=submission.connection.contact.healthproviderbase.healthprovider,
                patient=patient,
                message=message,
                valid=valid)
        birth_location = "a facility" if submission.eav.birth_place == 'FACILITY' else 'home'
        submission.response = "Thank you for registering the birth of %s. We have recorded that the birth took place at %s." % (patient_label(patient), birth_location)
        submission.save()
        return
    elif xform.keyword == 'death':
        days = submission.eav.death_age
        birthdate = datetime.date.today() - datetime.timedelta(days=days)
        patient = get_or_create_patient(health_provider, submission.eav.death_name, birthdate=birthdate, gender=submission.eav.death_gender, deathdate=datetime.date.today())
        valid = check_validity(xform.keyword, health_provider, patient)
        report = PatientEncounter.objects.create(
                submission=submission,
                reporter=health_provider,
                patient=patient,
                message=message,
                valid=valid)
        submission.response = "We have recorded the death of %s." % patient_label(patient)
        submission.save()
        return
    elif xform.keyword == 'epi':
        value_list = []
        for v in submission.eav.get_values():
            value_list.append("%s %d" % (disease_dict[v.attribute.name], v.value_int))
        value_list[len(value_list) - 1] = " and %s" % value_list[len(value_list) - 1]
        submission.response = "You reported %s" % ','.join(value_list)
        submission.save()
        return
    elif xform.keyword == 'home':
        value_list = []
        for v in submission.eav.get_values():
            if v.attribute.name in home_dict:
                value_list.append("%s %d" % (home_dict[v.attribute.name], v.value_int))
        value_list[len(value_list) - 1] = " and %s" % value_list[len(value_list) - 1]
        submission.response = "You reported %s" % ','.join(value_list)
        submission.save()
        return

xform_received.connect(xform_received_handler, weak=True)
