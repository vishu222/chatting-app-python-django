from django.contrib.auth.models import User
# from django.http.response import JsonResponse, HttpResponse
# from django.shortcuts import render, redirect
# from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
# from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from chat.models import User, Group, UserGroupMapping, Message
# from chat.forms import SignUpForm
# from chat.serializers import MessageSerializer, UserSerializer



@api_view(['GET', 'POST',])
def chat_view(request):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_403_FORBIDDEN, data={'error': 'You are not authorised'})
    user_groups = UserGroupMapping.objects.filter(user=request.user).values_list('group', flat=True)
    group_messages = Message.objects.filter(group__in=user_groups).order_by('-timestamp').values('sender__username', 'group__group_name', 'message')
    personal_messages = Message.objects.filter(Q(receiver=request.user) | (Q(Q(sender=request.user)&Q(group=None)))).order_by('-timestamp').values('sender__username', 'message')
    messages = {}
    group_messages_list = []
    personal_messages_list = []
    for grp_message in group_messages:
        group_messages_list.append(('{} ({}): {}'.format(grp_message.get('sender__username'), grp_message.get('group__group_name'), grp_message.get('message'))))

    for prsnl_message in personal_messages:
        personal_messages_list.append('{}: {}'.format(prsnl_message.get('sender__username'), prsnl_message.get('message') ))

    messages['group_messages']=group_messages_list
    messages['personal_messages']=personal_messages_list

    return Response(status=status.HTTP_200_OK, data={'response': messages})


@api_view(['GET', 'POST',])
def create_group(request, group_name):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_403_FORBIDDEN, data={'error': 'You are not authorised'})
    if request.method == "GET":
        # creating a chat group
        group_obj, created = Group.objects.get_or_create(group_name=group_name)
        if created:
            group_obj.creator=request.user
            group_obj.save()
            # create a UserGroupMapping entry as group creator by-default becomes a member of the group.
            UserGroupMapping.objects.get_or_create(user=request.user, group=group_obj)
            return Response(status=status.HTTP_200_OK, data={'response': 'A new chat group {} is created by {}'.format(group_name, request.user)})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'A group with a name {} already exists'.format(group_name)})


@api_view(['GET', 'POST',])
def join_group(request, group_name):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_403_FORBIDDEN, data={'error': 'You are not authorised.'})
    if request.method == "GET":
        try:
            group = Group.objects.get(group_name=group_name)
        except Group.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': '{} group does not exist.'.format(group_name)})

        # joining a chat group
        user_group_obj, created = UserGroupMapping.objects.get_or_create(user=request.user, group=group)
        if created:
            return Response(status=status.HTTP_200_OK, data={'response': '{} joined the group {} successfully.'.format(request.user, group.group_name)})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Already a member of this group.'})

@api_view(['GET', 'POST',])
def send_message_to_user_or_group(request):
    if request.method == 'POST':
        to_user = request.data.get('user', '')
        to_group = request.data.get('group', '')
        message = request.data.get('message', '')

        if not message:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'No message written.'})
        else:
            if to_user and to_group:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'send a message to either a user or a group.'})
            elif to_user:
                try:
                    receiver = User.objects.get(username=to_user)
                except User.DoesNotExist:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'receiver does not exist.'})
                #create message entry in the message table
                Message.objects.create(sender=request.user, receiver=receiver, message=message)
                return Response(status=status.HTTP_200_OK, data={'response': 'message sent to {} successfully.'.format(to_user)})
            else:
                try:
                    group = Group.objects.get(group_name=to_group)
                except DoesNotExist:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'The group does not exist.'})
                Message.objects.create(sender=request.user, group=group, message=message)
                return Response(status=status.HTTP_200_OK, data={'response': 'message sent to the group {} successfully.'.format(to_group)})





