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

from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db import models, connection, transaction
from django.contrib.auth.models import Permission as DjangoPermission
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth.models import Group as DjangoGroup

installation_completed_msg = 'Installation completed.'
upgrade_completed_msg = 'Upgrade completed.'

def install(request):
    """
    Initial TCMS database
    """
    # Start the installation if the FIRST_RUN in settings is True
    if settings.FIRST_RUN:
        if request:
            return HttpResponseRedirect(
                reverse('tcms.install.create_groups'),
                args = [True, ]
            )
        
        # Command line installation
        raw_input('Press enter key to start installation, or press Ctrl +C to interrupt.\n')
        print(create_groups({}))
        raw_input('Press enter key to continue to migrate the users.')
        print(port_users({}))
        return True
    
    # Otherwise break the installation steps
    return HttpResponse(installation_completed_msg)

def upgrade(request):
    """
    Upgrade 1.0 to 2.0
    """
    if settings.FIRST_RUN:
        if request:
            return HttpResponseRedirect(
                reverse('tcms.install.create_groups')
            )
            
        # Command line installation
        raw_input('Press enter key to start installation, or press Ctrl +C to interrupt.\n')
        print(create_groups({}))
        return True
    
    return HttpResponse(upgrade_completed_msg)

def create_groups(request, port_user = False, template_name='install/create_groups.html'):
    """
    Create the nercessery groups such as Tester and Administrator
    """
    if not settings.FIRST_RUN:
        if request:
            return HttpResponse(completed_msg)
        return completed_msg
    
    if not request:
        message = 'Starting to create groups for Tester and Administrtor\n\n'
        print(message)
    
    permissions = DjangoPermission.objects.all()
    
    # Create the Administrator group
    tester_group, create = DjangoGroup.objects.get_or_create(name='Tester')
    for permission in permissions:
        if permission.id > 30 and not permission.codename.startswith('delete_') \
        and permission.name.find('xml rpc') == -1:
            try:
                tester_group.permissions.add(permission)
                tester_group.save()
            except:
                pass
    
    # Create the Administrator group
    admin_group, create = DjangoGroup.objects.get_or_create(name='Administrator')
    for permission in permissions:
        if not permission.codename.startswith('delete_'):
            try:
                admin_group.permissions.add(permission)
                admin_group.save()
            except:
                pass
    
    # Render the web page for installation output
    if request:
        if port_user:
            return direct_to_template(request, template_name, {
                'tester_group': tester_group,
                'admin_group': admin_group,
            })
        else:
            return HttpResponse(upgrade_completed_msg)
    
    # Print out the output to console
    # if the user is not install with web service
    message += 'Create tester group successful with following permissions:\n\n'
    for permission in tester_group.permissions.all():
        message += '* ' + permission.name + '\n'
    message += 'Create administrator group successful with following permissions:\n\n'
    for permission in admin_group.permissions.all():
        message += '* ' + permission.name + '\n'
    
    return message

def port_users(request, template_name='install/port_users.html'):
    """
    Port the contents of profiles table into django_auth_user
    """
    from tcms.accounts.models import Profiles, Groups, UserGroupMap
    
    if not settings.FIRST_RUN:
        if request:
            return HttpResponse(completed_msg)
        return completed_msg
    
    if not request:
        message = 'Starting to migrate the users from profiles to auth_user table.\n'
        print(message)
    
    create_error_users = []
    for profile in Profiles.objects.all():
        try:
            user = DjangoUser.objects.create(
                id = profile.userid,
                username = profile.login_name.split('@')[0],
                email = profile.login_name,
                password = DjangoUser.objects.make_random_password(),
                is_active = profile.disabledtext and False or True,
            )
        except:
            create_error_users.append(profile.login_name)
    
    # Get the tester group
    try:
        tester_group = DjangoGroup.objects.get(name='Tester')
    except DjangoGroup.DoesNotExist:
        tester_group = None
        
    # Get the administrator group
    try:
        admin_group = DjangoGroup.objects.get(name='Administrator')
    except DjangoGroup.DoesNotExist:
        admin_group = None
    
    if not tester_group and not admin_group:
        return direct_to_template(request, template_name, {
            'create_user_errors': create_error_users,
            'message': 'Port user completed, no group added.'
        })
    
    # Add correct admin permission and group to users.
    for user in DjangoUser.objects.all():
        user_group_map = UserGroupMap.objects.filter(user__userid = user.id)
        user_group_map = user_group_map.values_list('group_id', flat=True)
        
        # 7 is the admin group id in groups table
        if 7 in user_group_map:
            admin_group and user.groups.add(admin_group)
            if settings.SET_ADMIN_AS_SUPERUSER:
                user.is_superuser = True
            user.is_staff = True
            user.save()
        
        # 15 is the tester group id in groups table
        if 15 in user_group_map:
            tester_group and user.groups.add(tester_group)
            user.is_staff = True
            user.save()
    
    # Render the web page for installation output
    if request:
        return direct_to_template(request, template_name, {
            'create_user_errors': create_error_users,
        })
    
    message = ''
    # Print out the output to console
    # if the user is not install with web service
    if create_error_users:
        message += 'Following users are failed to migrate.\n'
        for user in create_error_users:
            message += '* ' + user + '\n'
    
    message += 'Installation completed.\n\n'
    message += 'Please do not forget to set FIRST_RUN to False in settings file.\n'
    
    return message

if __name__ == '__main__':
    install({})
