from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.http import JsonResponse
from django.http import HttpResponse
from documents.models import Document, File
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.utils.html import escape
from django.core import serializers
from django.conf import settings
from pyelasticsearch import ElasticSearch, exceptions
from django.views.decorators.csrf import csrf_exempt
import requests
import json
#from logging.signals import log_document_metadata_request_error

es = ElasticSearch(settings.ELASTICSEARCH_URL)
ANNOTATION_TYPE = 'annotation'
PAGE_SIZE = 1000


@login_required
@require_http_methods(["GET", "PUT"])
def targets(request):
    target_list = Document.objects.values('id')
    return HttpResponse(json.dumps([target for target in target_list]),status=200,content_type='application/json; charset=utf8')
    #return JsonResponse(target_list,safe=False)

@login_required
@require_http_methods(["GET", "PUT"])
def target(request,target_pk):
    if request.method == 'GET':
        if Document.objects.filter(id=target_pk).exists():
            document = Document.objects.get(id=target_pk)
            data = serializers.serialize('json', [document])
            struct = json.loads(data)
            return HttpResponse([json.dumps(struct[0])],status=200,content_type='application/json; charset=utf8')
            #f = document.attached_file
            # return raw data
            #return HttpResponse(str(f.raw_data),status=200, content_type=f.content_type + '; charset=utf-8')
        else:
            return HttpResponse(status=404)
    else:
        return HttpResponse(status=404)

@login_required
@csrf_exempt
@require_http_methods(["GET", "PUT"])
def annotations(request,target_pk):
    if request.method == 'GET':
        try:
            annotation = es.search("uri:"+target_pk)
        except:
            return HttpResponse(status=500)
        else:
            return JsonResponse([annotation['_source'] for annotation in annotation['hits']['hits']], safe=False)
    else:
        return HttpResponse(status=404)


@login_required
@csrf_exempt
@require_http_methods(["GET", "POST"])
def annotation(request, target_pk, annotation_pk):
    if request.method == 'GET':
        try:
            annotation = es.search("uri:"+target_pk+" AND "+"id:"+annotation_pk,index=settings.ELASTICSEARCH_INDEX)
        except:
            return HttpResponse(status=500)
        else:
            return JsonResponse(annotation, safe=False)
            return JsonResponse(annotation['hits']['hits'][0]['_source'], safe=False)
    elif request.method == 'POST':
        target = es.search("uri:"+target_pk,index=settings.ELASTICSEARCH_INDEX)
        if(target['hits']['total']!=0):
            annotation = es.search("uri:"+target_pk+" AND "+"id:"+annotation_pk,index=settings.ELASTICSEARCH_INDEX)
            if(annotation['hits']['total']==0):
                data = json.loads(request.body)
                if(("@context" in data) and ("id" in data) and ("type" in data) and ("target" in data)):
                    data['uri']=target_pk
                    es.index(settings.ELASTICSEARCH_INDEX,ANNOTATION_TYPE,doc=data,id=data['id'])
                    return HttpResponse(status=201)
                else:
                    return HttpResponse(status=408)
            else:
                return HttpResponse(status=409)
        else:
            return HttpResponse(status=404)
    else:
        return HttpResponse(status=404)
