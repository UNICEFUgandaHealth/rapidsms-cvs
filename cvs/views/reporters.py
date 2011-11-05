#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.template import RequestContext
from django.shortcuts import (render_to_response, get_object_or_404)
from django.http import HttpResponse
from healthmodels.models.HealthProvider import HealthProvider, \
    HealthProviderBase
from healthmodels.models import HealthFacility
from cvs.forms import ReporterForm
from django.contrib.auth.decorators import login_required
from generic.views import generic_row
from rapidsms.contrib.locations.models import Location


@login_required
def deleteReporter(request, reporter_pk):
    reporter = get_object_or_404(HealthProviderBase, pk=reporter_pk)
    if request.method == 'POST':
        reporter.delete()
    return HttpResponse(status=200)

@login_required
def editReporter(request, reporter_pk):
    reporter = get_object_or_404(HealthProviderBase, pk=reporter_pk)
    reporter_form = ReporterForm(instance=reporter)
    if request.method == 'POST':
        reporter_form = ReporterForm(instance=reporter,
                data=request.POST)
        if reporter_form.is_valid():
            reporter_form.save()
            return generic_row(request, model=HealthProviderBase, pk=reporter_pk, partial_row='/cvs/reporter/partials/reporter_row.html')
        else:
            return render_to_response('cvs/reporter/partials/edit_reporter.html'
                    , {'reporter_form': reporter_form, 'reporter'
                    : reporter},
                    context_instance=RequestContext(request))
    else:
        return render_to_response('cvs/reporter/partials/edit_reporter.html',
                                  {'reporter_form': reporter_form,
                                  'reporter': reporter},
                                  context_instance=RequestContext(request))


def editReporterLocations(request, reporter_pk, district_pk=None):
    reporter = get_object_or_404(HealthProviderBase, pk=reporter_pk)
    locations = reporter.reporting_location or reporter.location
    if not locations:
        return HttpResponse(status=404)
    locations = locations.get_descendants(include_self=True)
    if district_pk:
        district = get_object_or_404(Location, pk=district_pk)
        locations = district.get_descendants(include_self=True)
    if reporter.reporting_location and reporter.reporting_location.type.name != 'district':
        village_val = reporter.reporting_location.name
    else:
        village_val = reporter.village_name
    return render_to_response('cvs/reporter/partials/edit_reporter_locations.html',
                              {'locations': locations,
                               'village_val': village_val,
                               'reporter': reporter},
                              context_instance=RequestContext(request))


def editReporterFacilities(request, reporter_pk, district_pk=None):
    reporter = get_object_or_404(HealthProviderBase, pk=reporter_pk)
    locations = reporter.reporting_location or reporter.location
    facilities = HealthFacility.objects.all()
    if not locations:
        return HttpResponse(status=404)
    locations = locations.get_descendants(include_self=True)
    if district_pk:
        district = get_object_or_404(Location, pk=district_pk)
        locations = district.get_descendants(include_self=True)
        facilities = HealthFacility.objects.filter(catchment_areas__in=locations).distinct()
    return render_to_response('cvs/reporter/partials/edit_reporter_facilities.html',
                              {'facilities': facilities,
                               'reporter': reporter},
                              context_instance=RequestContext(request))
