import graphene
import qrcode

from io import BytesIO

from django.conf import settings
from django.utils.crypto import get_random_string
from django.core.files.base import ContentFile

from graphene_django import DjangoObjectType

from app.decorators import login_required, method_decorator
from .models import Case, Video


class CaseNode(DjangoObjectType):
    class Meta:
        model = Case
        interfaces = (graphene.relay.Node, )
        filter_fields = ['token']

    def resolve_qrcode(self, *args, **kwargs):
        return settings.SERVER_URL_PREFIX + str(self.qrcode)


class VideoNode(DjangoObjectType):
    class Meta:
        model = Video
        interfaces = (graphene.relay.Node, )
        filter_fields = []


class Query:
    pass


class CreateCase(graphene.relay.ClientIDMutation):
    case = graphene.Field(CaseNode)

    class Input:
        name = graphene.String(required=True)
        text = graphene.String(required=True)

    @method_decorator(login_required)
    def mutate_and_get_payload(self, info, **input):
        name = input.get('name')
        text = input.get('text')
        token = get_random_string(length=16)

        qr_img = qrcode.make(settings.SERVER_URL_PREFIX +
                             'case/{}'.format(token))

        f = BytesIO()
        qr_img.save(f, format='png')

        case = Case.objects.create(
            name=name,
            text=text,
            token=token,
        )

        case.qrcode.save(token + '.png', ContentFile(f.getvalue()))
        case.members.set([info.context.user])

        f.close()

        return CreateCase(case=case)


class Mutation:
    create_case = CreateCase.Field()
