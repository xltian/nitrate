# -*- coding: utf-8 -*-
#
# Nitrate is copyright 2010 Red Hat, Inc.
#
# Nitrate is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version. This program is distributed in
# the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranties of TITLE, NON-INFRINGEMENT,
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# The GPL text is available in the file COPYING that accompanies this
# distribution and at <http://www.gnu.org/licenses>.
#
# Authors:
#   Xuqing Kuang <xkuang@redhat.com>

try:
    from django.db import IntegrityError
except:
    pass

from django.utils.simplejson import dumps as json_dumps

from django.contrib.auth.decorators import user_passes_test
from django.views.generic.simple import direct_to_template
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils import simplejson
from django.core.urlresolvers import reverse

from tcms.apps.management.models import TCMSEnvGroup, TCMSEnvProperty, \
        TCMSEnvGroupPropertyMap, TCMSEnvValue

MODULE_NAME = "management"

# Create your views here.

def environment_groups(request, template_name = 'environment/groups.html'):
    """
    Environements list
    """

    env_groups = TCMSEnvGroup.objects
    # Initial the response to browser
    ajax_response = { 'response': 'ok' }

    # Add action
    if request.REQUEST.get('action') == 'add':
        if not request.user.has_perm('management.add_tcmsenvgroup'):
            ajax_response['response'] = 'Permission denied.'
            return HttpResponse(json_dumps(ajax_response))

        # Get the group name of envrionment from javascript
        if not request.REQUEST.get('name'):
            ajax_response['response'] = 'Environment group name is required.'
            return HttpResponse(json_dumps(ajax_response))

        try:
            env = env_groups.create(
                name = request.REQUEST['name'],
                manager_id = request.user.id,
                modified_by_id = None,
            )
            env.log_action(
                who = request.user,
                action = 'Initial env group %s' % env.name
            )
            ajax_response['id'] = env.id
            return HttpResponse(json_dumps(ajax_response))
        except IntegrityError, error:
            if error[1].startswith('Duplicate'):
                ajax_response['response'] = 'Environment group named \'%s\' already exists, please select another name.' % request.REQUEST['name']
            else:
                ajax_response['response'] = error[1]

            return HttpResponse(json_dumps(ajax_response))
        except:
            ajax_response['response'] = 'Unknown error.'
            return HttpResponse(json_dumps(ajax_response))

    # Del action
    if request.REQUEST.get('action') == 'del':
        if request.REQUEST.get('id'):
            try:
                env = env_groups.get(id = request.REQUEST['id'])
                manager_id = env.manager_id
                if (request.user.id !=  manager_id):
                    if not request.user.has_perm('management.delete_tcmsenvgroup'):
                        ajax_response['response']='Permission denied.'
                        return HttpResponse(json_dumps(ajax_response))

                env.delete()
                ajax_response['response']='ok'
            except TCMSEnvGroup.DoesNotExist, error:
                raise Http404(error)

            try:
                env_group_property_map = env_groups.filter(
                    group_id = request.REQUEST['id']
                )
                env_group_property_map.delete()
            except:
                pass
            return HttpResponse(json_dumps(ajax_response))
        else:
            pass

        if not request.user.has_perm('management.delete_tcmsenvgroup'):
            ajax_response['response'] = 'Permission denied.'
            return HttpResponse(json_dumps(ajax_response))

    # Modify actions
    if request.REQUEST.get('action') == 'modify':
        if not request.user.has_perm('management.change_tcmsenvgroup'):
            return HttpResponse("Permission denied")

        try:
            env = env_groups.get(id = request.REQUEST['id'])
            if request.REQUEST.get('status') in ['0', '1']:
                env.is_active = int(request.REQUEST['status'])
                env.log_action(
                    who = request.user,
                    action = 'Change env group status to %s' % env.is_active
                )
            else:
                return HttpResponse('Argument illegel')
            env.save()
        except TCMSEnvGroup.DoesNotExist, error:
            raise Http404(error)

    # Search actions
    if request.REQUEST.get('action') == 'search':
        if request.REQUEST.get('name'):
            env_groups = env_groups.filter(
                name__icontains = request.REQUEST['name']
            )
        else:
            env_groups = env_groups.all()
    else:
        env_groups = env_groups.all().order_by('is_active')

    return direct_to_template(request, template_name, {
        'environments': env_groups
    })

@user_passes_test(lambda u: u.has_perm('management.change_tcmsenvgroup'))
def environment_group_edit(request, template_name = 'environment/group_edit.html'):
    """
    Assign properties to environment group
    """

    # Initial the response
    response = ''

    try:
        environment = TCMSEnvGroup.objects.get(id = request.REQUEST.get('id', None))
    except TCMSEnvGroup.DoesNotExist, error:
        raise Http404

    try:
        de = TCMSEnvGroup.objects.get(name = request.REQUEST.get('name'))
        if environment != de:
            response = 'Duplicated name already exists, please change to another name.'
            return direct_to_template(request, template_name, {
                'environment': environment,
                'properties': TCMSEnvProperty.get_active(),
                'selected_properties': environment.property.all(),
                'message': response,
            })
    except TCMSEnvGroup.DoesNotExist, error:
        pass

    if request.REQUEST.get('action') == 'modify':   # Actions of modify
        if environment.name != request.REQUEST['name']:
            environment.name = request.REQUEST['name']
            environment.log_action(
                who = request.user,
                action = 'Modify name %s from to %s' % (environment.name, request.REQUEST['name'])
            )

        if environment.is_active != request.REQUEST.get('enabled', False):
            environment.is_active = request.REQUEST.get('enabled', False)
            environment.log_action(
                who = request.user,
                action = 'Change env group status to %s' % environment.is_active
            )

        environment.modified_by_id = request.user.id
        environment.save()

        # Remove all of properties of the group.
        TCMSEnvGroupPropertyMap.objects.filter(
            group__id = environment.id,
        ).delete()

        # Readd the property to environemnt group and log the action
        for property_id in request.REQUEST.getlist('selected_property_ids'):
            TCMSEnvGroupPropertyMap.objects.create(
                group_id = environment.id,
                property_id = property_id,
            )

        environment.log_action(
            who = request.user,
            action = 'Properties changed to %s' % (
                ', '.join(environment.property.values_list('name', flat=True))
            )
        )

        response = 'Environment group saved successfully.'

    return direct_to_template(request, template_name, {
        'environment': environment,
        'properties': TCMSEnvProperty.get_active(),
        'selected_properties': environment.property.all(),
        'message': response,
    })

def environment_properties(request, template_name = 'environment/property.html'):
    """
    Edit environemnt properties and values belong to
    """

    # Initial the ajax response
    ajax_response = { 'response': 'ok' }
    message = ''

    # Actions of create properties
    if request.REQUEST.get('action') == 'add':
        if not request.user.has_perm('management.add_tcmsenvproperty'):
            ajax_response['response'] = 'Permission denied'
            return HttpResponse(json_dumps(ajax_response))

        if not request.REQUEST.get('name'):
            response = { 'response': 'Property name is required' }
            return HttpResponse(json_dumps(ajax_response))

        try:
            new_property = TCMSEnvProperty.objects.create(
                name = request.REQUEST['name']
            )
            ajax_response['id'] = new_property.id
            ajax_response['name'] = new_property.name

        except IntegrityError, error:
            if error[1].startswith('Duplicate'):
                ajax_response['response'] = 'Environment proprerty named \'%s\' already exists, please select another name.' % request.REQUEST['name']
            else:
                ajax_response['response'] = error[1]

            return HttpResponse(json_dumps(ajax_response))

        return HttpResponse(json_dumps(ajax_response))

    # Actions of edit a exist properties
    if request.REQUEST.get('action') == 'edit':
        if not request.user.has_perm('management.change_tcmsenvproperty'):
            ajax_response['response'] = 'Permission denied'
            return HttpResponse(json_dumps(ajax_response))

        if not request.REQUEST.get('id'):
            ajax_response['response'] = 'ID is required'
            return HttpResponse(json_dumps(ajax_response))

        try:
            env_property = TCMSEnvProperty.objects.get(id = request.REQUEST['id'])
            env_property.name = request.REQUEST.get('name', env_property.name)
            try:
                env_property.save()
            except IntegrityError, error:
                ajax_response['response'] = error[1]
                return HttpResponse(json_dumps(ajax_response))

        except TCMSEnvProperty.DoesNotExist, error:
            ajax_response['response'] = error[1]

        return HttpResponse(json_dumps(ajax_response))

    # Actions of remove properties
    if request.REQUEST.get('action') == 'del':
        if not request.user.has_perm('management.delete_tcmsenvproperty'):
            message = 'Permission denied'

        if request.user.has_perm('management.delete_tcmsenvproperty') and request.REQUEST.get('id'):
            try:
                env_group_property_map = TCMSEnvGroupPropertyMap.objects.filter(
                    property__id__in = request.REQUEST.getlist('id')
                )
                env_group_value_map = TCMSEnvGroupPropertyMap.objects.filter(
                    property__id__in = request.REQUEST.getlist('id')
                )
                env_group_property_map and env_group_property_map.delete()
                env_group_value_map and env_group_value_map.delete()
            except:
                pass

            try:
                env_properties = TCMSEnvProperty.objects.filter(
                    id__in = request.REQUEST.getlist('id')
                )
                message = 'Remove test properties %s successfully.' % '\', \''.join(
                    env_properties.values_list('name', flat=True)
                )
                env_properties.delete()
            except TCMSEnvProperty.DoesNotExist, error:
                message = error[1]

    # Actions of remove properties
    if request.REQUEST.get('action') == 'modify':
        if not request.user.has_perm('management.change_tcmsenvproperty'):
            message = 'Permission denied'

        if request.user.has_perm('management.change_tcmsenvproperty') and request.REQUEST.get('id'):
            try:
                env_properties = TCMSEnvProperty.objects.filter(
                    id__in = request.REQUEST.getlist('id')
                )

                if request.REQUEST.get('status') in ['0', '1']:
                    for env_property in env_properties:
                        env_property.is_active = int(request.REQUEST['status'])
                        env_property.save()

                    message = 'Modify test properties status \'%s\' successfully.' % '\', \''.join(
                        env_properties.values_list('name', flat=True)
                    )
                else:
                    message = 'Argument illegel'

            except TCMSEnvProperty.DoesNotExist, error:
                message = error[1]

            try:
                env_group_property_map = TCMSEnvGroupPropertyMap.objects.filter(
                    property__id__in = request.REQUEST.getlist('id')
                )
                env_group_value_map = TCMSEnvGroupPropertyMap.objects.filter(
                    property__id__in = request.REQUEST.getlist('id')
                )
                env_group_property_map and env_group_property_map.delete()
                env_group_value_map and env_group_value_map.delete()
            except:
                pass

    if request.is_ajax():
        return HttpResponse('Unknown action')

    return direct_to_template(request, template_name, {
        'message': message,
        'properties': TCMSEnvProperty.objects.all().order_by('-is_active')
    })

def environment_property_values(request, template_name = 'environment/ajax/property_values.html'):
    """
    List values of property
    """
    message = ''
    duplicated_property_value = []

    if not request.REQUEST.get('property_id'):
        return HttpResponse('Property ID should specify')

    try:
        property = TCMSEnvProperty.objects.select_related('value').get(
            id = request.REQUEST['property_id']
        )
    except TCMSEnvProperty.DoesNotExist, error:
        return HttpResponse(error)

    if request.REQUEST.get('action') == 'add' and request.REQUEST.get('value'):
        if not request.user.has_perm('management.add_tcmsenvvalue'):
            return HttpResponse('Permission denied')

        for value in request.REQUEST['value'].split(','):
            try:
                property.value.create(
                    value = value
                )
            except IntegrityError, error:
                if error[1].startswith('Duplicate'):
                    duplicated_property_value.append(value)

    if request.REQUEST.get('action') == 'edit' and request.REQUEST.get('id'):
        if not request.user.has_perm('management.change_tcmsenvvalue'):
            return HttpResponse('Permission denied')

        try:
            property_value = property.value.get(
                id = request.REQUEST['id']
            )
            property_value.value = request.REQUEST.get(
                'value', property_value.value
            )
            try:
                property_value.save()
            except IntegrityError, error:
                if error[1].startswith('Duplicate'):
                    duplicated_property_value.append(property_value.value)

        except TCMSEnvValue.DoesNotExist, error:
            return HttpResponse(error[1])

    if request.REQUEST.get('action') == 'modify' and request.REQUEST.get('id'):
        if not request.user.has_perm('management.change_tcmsenvvalue'):
            return HttpResponse('Permission denied')

        values = property.value.filter(id__in = request.REQUEST.getlist('id'))
        if request.REQUEST.get('status') in ['0', '1']:
            for value in values:
                value.is_active = int(request.REQUEST['status'])
                value.save()
        else:
            return HttpResponse('Argument illegel')

    if duplicated_property_value:
        message = 'Value(s) named \'%s\' already exists in this property, please select another name.' % '\', \''.join(
            duplicated_property_value
        )

    values = property.value.all()
    return direct_to_template(request, template_name, {
        'property': property,
        'values': values,
        'message': message,
    })
