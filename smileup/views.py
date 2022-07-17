import json
import os

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
#from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls import reverse
from django import forms
from django.shortcuts import get_object_or_404, redirect

from .models import Post, Bot_info
from .bot import parse_input_message

def index(request):
    return render(request, "index.html")


#@login_required
def db(request):
    posts = Post.objects.all()
    return render(request, "db.html", {"posts": posts})

class CSVForm(forms.Form):
    data = forms.CharField(widget=forms.Textarea)

def add_bunch_quotes(data):
    data = data.split("\r\n")
    names = data[0].split(";")  # TODO в импортируемых текстах не должно быть точек с запятой
    quote_id = names.index("quote")
    link_id = names.index("link")
    nick_id_id = names.index("nick_id")
    status_id = names.index("status")
    for string in data[1:]:
        d = string.split(";")
        post = Post.objects.create(quote=d[quote_id], link=d[link_id],
                                   nick_id=d[nick_id_id], status=d[status_id])

def csv(request, code=""):
    if code == os.getenv("SECRET_URL"):
        if request.method == "POST":
            data = PostForm(request.POST).data['data']
            add_bunch_quotes(data)
        posts = Post.objects.all()
        form = CSVForm()
        return render(request, "csv.html", {"posts": posts, "form": form})
    else:
        return HttpResponse('Такой страницы нет, совсем нет.', status=404)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('quote', 'link',)


def quote(request, id, code=""):
    post = get_object_or_404(Post, pk=id)
    if post and post.code == code:
        if request.method == "GET":
            form = PostForm(instance=post)
        else:
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                try:
                    post = form.save(commit=False)
                    post.status = Post.EDIT
                    post.save()
                except:
                    return render(request, "post_edit.html", {"form": form, "error": True})
            return render(request, "post_edit.html", {"form": form, "edit_post": True}) #redirect('db')
        return render(request, "post_edit.html", {"form": form})
    else:
        return HttpResponse('Такой записи нет, либо вы не можете ее редактировать', status=404)


@csrf_exempt
def got_message(request, param="qu"):
    if request.method != "POST":
        return HttpResponse('только POST-запросы, и никак иначе', status=404)

    bot_info = Bot_info.objects.filter(token=param).first()
    if bot_info: # TODO проверку на Smile_up, на случай нескольких ботов в базе данных
        data = json.loads(request.body)
        parse_input_message(request, data, bot_info)
        return HttpResponse("OK", status=200)

    return HttpResponse(status=404)
