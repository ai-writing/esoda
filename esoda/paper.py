from django.conf import settings
from django.http import Http404


class Corpus:
    class Meta:
        pk = '_id'
        db = ('common', 'corpora')
    # TODO


class UploadRecord:
    class Meta:
        pk = '_id'
        db = ('common', 'uploads')
    # TODO


class UploadFile:
    class Meta:
        pk = '_id'
        db = ('common', 'files')
    # TODO


class UserProfile:
    class Meta:
        pk = '_id'
        db = ('common', 'users')
    # TODO


class DblpPaper:
    class Meta:
        pk = '@id'
        db = ('esl', 'papers')
    # TODO


class DblpVenue:
    class Meta:
        pk = '_id'
        db = ('esl', 'venues')
    # TODO


class Field:
    class Meta:
        pk = '_id'
        db = ('esl', 'fields')
    # TODO


def mongo_get_object(type_object, projection=None, **kwargs):
    if 'pk' in kwargs:
        kwargs[type_object.Meta.pk] = kwargs['pk']
        del kwargs['pk']
    database_name, collection_name = type_object.Meta.db
    o = settings.MONGODB[database_name][collection_name].find_one(kwargs, projection)
    if o:
        o['pk'] = o[type_object.Meta.pk]
    return o


def mongo_get_objects(type_object, projection=None, **kwargs):
    if 'pks' in kwargs:
        kwargs[type_object.Meta.pk] = {'$in': kwargs['pks']}
        del kwargs['pks']
    database_name, collection_name = type_object.Meta.db
    o = settings.MONGODB[database_name][collection_name].find(kwargs, projection)
    res = {}
    for i in o:
        res[i[type_object.Meta.pk]] = i
    return res


def mongo_get_object_or_404(type_object, projection=None, **kwargs):
    o = mongo_get_object(type_object, projection, **kwargs)
    if not o:
        database_name, collection_name = type_object.Meta.db
        raise Http404('No match found in %s.%s.' % (database_name, collection_name))
    return o
