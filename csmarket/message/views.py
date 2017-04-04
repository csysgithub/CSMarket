#-*-coding:utf-8-*-
from django.shortcuts import render,render_to_response,HttpResponseRedirect
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from message.models import Message,Cate,Mwords
import time
# Create your views here.

#发布需求/服务
@csrf_exempt
def postService(request,cate):
    if request.method == 'POST':
        title = request.POST.get('biaoti')
        image = request.POST.get('fengmian')
        leibie = request.POST.get('leibie')
        price = request.POST.get('baojia')
        miaoshu = request.POST.get('miaoshu')

        now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        mess = Message(mess_title=title,mess_image=image,mess_author=request.user,mess_time=now_time,\
                       mess_xuorfu=cate,mess_price=price,mess_seenum=0,mess_content=miaoshu)
        mess.mess_cate_id=Cate.objects.get(cate_name=leibie).cate_num
        mess.save()

        return render_to_response('post_service.html', {
            'user_name': request.user,
            'cate': cate,
            'flag': 1 if cate == "服务" else 0,
        })
    else:
        if request.user.is_authenticated:
            return render_to_response('post_service.html',{
                'user_name': request.user,
                'cate': cate,
                'flag': 1 if cate=="服务" else 0,
            })
        else:
            request.session['error'] = "你还没有登录，请先登录！"
            referer = request.META['HTTP_REFERER']  # 获取网页访问来源
            return HttpResponseRedirect(referer)

#编辑需求
def editService(request,cate):

    return render_to_response("edit_service.html",{
        'cate': cate,
        'flag': 1 if cate == "服务" else 0,
    })