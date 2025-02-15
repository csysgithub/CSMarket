#-*-coding:utf-8-*-
from django.shortcuts import render,render_to_response,HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from message.models import Message,Cate,Mwords,DMwords,DMessage,DCate
import time
from django.core.files.storage import FileSystemStorage
from logre.models import User,UserSee
from django.db.models import Q
from django.http import HttpResponseBadRequest
# Create your views here.

#发布需求/服务
@csrf_exempt
def postService(request,cate):
    # if request.method == 'POST':
    #     title = request.POST.get('biaoti')
    #     #保存图片，以url形式存储到数据库中
    #     image = request.FILES["fengmian"]
    #     fs = FileSystemStorage()
    #     filename = fs.save("fengmian/"+image.name, image)
    #     uploaded_file_url = fs.url(filename)

    #     leibie = request.POST.get('leibie')
    #     price = request.POST.get('baojia')
    #     miaoshu = request.POST.get('miaoshu')


    if request.method == 'POST':
        title = request.POST.get('biaoti')
        leibie = request.POST.get('leibie')
        miaoshu = request.POST.get('miaoshu')

        if not title:
            return HttpResponseBadRequest('标题不能为空')
        if not leibie:
            return HttpResponseBadRequest('类别不能为空')
        if not miaoshu:
            return HttpResponseBadRequest('描述不能为空')

        if 'fengmian' not in request.FILES:
            return HttpResponseBadRequest('必须上传一张图片')
        image = request.FILES["fengmian"]
        if not image:
            return HttpResponseBadRequest('图片不能为空')

        price = request.POST.get('baojia')
        if not price:
            price = 0
        #保存图片，以url形式存储到数据库中
        fs = FileSystemStorage()
        filename = fs.save("fengmian/"+image.name, image)
        uploaded_file_url = fs.url(filename)

        # 这里要根据类别来定，因为服务/需求 是公用一个数据表， 而代办中心是一个单独的数据表
        if cate=="代办":
            bool_rep = DMessage.objects.filter(dmess_title=title, dmess_author=request.COOKIES.get('name'))
        else:
            bool_rep = Message.objects.filter(mess_title=title, mess_author=request.COOKIES.get('name'))

        if bool_rep:
            if Message.objects.filter(mess_title=title,mess_author=request.COOKIES.get('name')):
                return render_to_response('post_service.html',{
                    'user_name': request.COOKIES.get('name'),
                    'cate': cate,
                    'title': title,
                    'leibie': leibie,
                    'price': price,
                    'miaoshu': miaoshu,
                    'repeat_error': '你已发表过该标题的需求或者服务！'
                })

        now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        #根据类别来判断映射那哪个数据库模型
        if cate == "代办":
            mess = DMessage(dmess_title=title, dmess_image=uploaded_file_url, dmess_author=request.COOKIES.get('name'), dmess_time=now_time, \
                           dmess_price=price, dmess_seenum=0, dmess_content=miaoshu)
            mess.dmess_cate_id = DCate.objects.get(dcate_name=leibie).dcate_num
        else:
            mess = Message(mess_title=title,mess_image=uploaded_file_url,mess_author=request.COOKIES.get('name'),mess_time=now_time,\
                       mess_xuorfu=cate,mess_price=price,mess_seenum=0,mess_content=miaoshu)
            mess.mess_cate_id=Cate.objects.get(cate_name=leibie).cate_num
        mess.save()

        return HttpResponseRedirect("/message/oneService/%s/%s/%s" % (request.COOKIES.get('name'),cate,title))
        # return render_to_response('services_one.html', {
        #     'user_name': request.user,
        #     'cate': cate,
        #     'flag': 1 if cate == "服务" else 0,
        # })
    else:
        uname = request.COOKIES.get('name','')
        if uname:
            user = User.objects.get(username=uname)
            # 如果用户已经被认证，且已经审核通过
            # if user and user.user_isValid:
            #     cate_list =DCate.objects.all() if cate=="代办" else Cate.objects.all()
            #     return render_to_response('post_service.html',{
            #         'user_name': request.COOKIES.get('name'),
            #         'cate': cate,
            #         'cate_list': cate_list,
            #     })
            # # 如果未通过审核，提示先去补充个人信息
            # elif not user.user_isValid:
            #     request.session['not_auth_error'] = "你还没有进行信息认证，请先去认证信息"
            #     try:
            #         referer = request.META['HTTP_REFERER']  # 获取网页访问来源
            #         return render_to_response('prefect.html', {
            #             'not_auth_error': '你还没有通过信息认证，请完善或者修改信息!',
            #             'referer': referer,
            #             'user': User.objects.get(username=request.COOKIES.get('name','')),
            #         })
            #     except:
            #         return render_to_response('404.html', {
            #             'error': request.session.get('not_auth_error', default=None)
            #         })
            cate_list =DCate.objects.all() if cate=="代办" else Cate.objects.all()
            return render_to_response('post_service.html',{
                 'user_name': request.COOKIES.get('name'),
                  'cate': cate,
                  'cate_list': cate_list,
            })            
        else:
            request.session['error'] = "你还没有登录，请先登录！"
            try:
                referer = request.META['HTTP_REFERER']  # 获取网页访问来源
                # return HttpResponseRedirect(referer)
                return render_to_response('login.html',{
                    'from': referer,
                    'login_error': request.session.get('error'),
                })
            except:
                return render_to_response('404.html',{
                    'error':request.session.get('error',default=None)
                })
#编辑需求
@csrf_exempt
def edit(request,name,cate,title):
    uname = name
    if request.method == 'POST':
        # #保存图片，以url形式存储到数据库中
        # image = request.FILES["fengmian"]
        # fs = FileSystemStorage()
        # filename = fs.save("fengmian/"+image.name, image)
        # uploaded_file_url = fs.url(filename)
        new_title = request.POST.get('biaoti')
        leibie = request.POST.get('leibie')
        price = request.POST.get('baojia')
        miaoshu = request.POST.get('miaoshu')
        hezuo = request.POST.get('tuoguan')
        ifsuccess = request.POST.get('jiaoyi')

        now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        #根据类别来判断映射那哪个数据库模型
        if cate == "代办":

            mess = DMessage.objects.get(dmess_author=uname,dmess_title=title,dmess_cate_id=DCate.objects.get(dcate_name=leibie).dcate_num)
            mess.dmess_title = new_title
            # mess.dmess_cate = leibie
            mess.dmess_price = price
            mess.dmess_content = miaoshu
            mess.dmess_hezuo = hezuo
            mess.dmess_ifsuccess = ifsuccess
            mess.dmess_time = now_time

            mess.save()
        else:
            mess = Message.objects.get(mess_author=uname, mess_title=title, mess_cate_id=Cate.objects.get(cate_name=leibie).cate_num)
            mess.mess_title = new_title
            # mess.mess_cate = leibie
            mess.mess_price = price
            mess.mess_content = miaoshu
            mess.mess_hezuo = hezuo
            mess.mess_ifsuccess = ifsuccess
            mess.mess_time = now_time

            mess.save()
            # mess.mess_cate_id=Cate.objects.get(cate_name=leibie).cate_num

        return HttpResponseRedirect("/message/oneService/%s/%s/%s" % (request.COOKIES.get('name'),cate,new_title))
    else:
        if cate=='代办':
            mess = DMessage.objects.get(dmess_author=uname,dmess_title=title)
        else:
            mess = Message.objects.get(mess_author=uname,mess_title=title)

        return render_to_response("edit_service.html",{
            'user_name': uname,
            'cate': cate,
            'title': title,
            'mess': mess,
        })

#删除信息 同时删除用户浏览表中的信息
def delete(request,cate,title):
    if cate=='代办':
        DMessage.objects.get(dmess_author=request.COOKIES.get('name'),dmess_title=title).delete()
        UserSee.objects.get(see_people=request.COOKIES.get('name'),title=title).delete()
    else:
        Message.objects.get(mess_author=request.COOKIES.get('name'),mess_title=title).delete()
        UserSee.objects.get(see_people=request.COOKIES.get('name'),title=title).delete()
    return HttpResponseRedirect('/index')

#查看单个需求或者服务
def oneService(request,user,cate,title):
    # 记录浏览信息
    if request.COOKIES.get('name',''):
        see_name = request.COOKIES.get('name','')
        now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # 查询message 表中的image
        if cate=='代办':
            image = DMessage.objects.get(dmess_author=user,dmess_title=title).dmess_image
        else:
            image = Message.objects.get(mess_author=user,mess_title=title).mess_image
        # 如果已经浏览过，则更新即可
        try:
            if UserSee.objects.get(title=title, see_people=see_name):
                see_update = UserSee.objects.get(title=title, see_people=see_name)
                see_update.time = now_time
                see_update.save()
        except:
            see = UserSee(title=title,image=image,pub_author=user,see_people=see_name,cate=cate,time=now_time)
            see.save()

    # 获取该title对应的message的信息
    if cate == "代办":
        one = DMessage.objects.get(dmess_title=title, dmess_author=user)
        one.dmess_seenum = one.dmess_seenum + 1
        one.save()
        # 获取该message对应的发布者的联系信息
        per = User.objects.get(username=one.dmess_author)
    else:
        one = Message.objects.get(mess_title=title,mess_author=user)
        one.mess_seenum = one.mess_seenum + 1
        one.save()
        # 获取该message对应的发布者的联系信息
        per = User.objects.get(username=one.mess_author)

    if request.COOKIES.get('name')==user:
        flag= 1
    return render_to_response('services_one.html',{
        'user_name': request.COOKIES.get('name',''),
        'title': one.dmess_title if cate=="代办" else one.mess_title,
        'fengmian': one.dmess_image if cate=="代办" else one.mess_image,
        'smallcate': one.dmess_cate if cate=="代办" else one.mess_cate,
        'price': one.dmess_price if cate=="代办" else one.mess_price,
        'time': one.dmess_time if cate=="代办" else one.mess_time,
        'author': one.dmess_author if cate=="代办" else one.mess_author,
        'seenum': one.dmess_seenum if cate=="代办" else one.mess_seenum,
        'totalnum': one.dmess_totalnum if cate=="代办" else one.mess_totalnum,
        'compeletenum': one.dmess_compeletenum if cate=="代办" else one.mess_compeletenum,
        'tuo': one.dmess_hezuo if cate=="代办" else one.mess_hezuo,
        'iforno': one.dmess_ifsuccess if cate=="代办" else one.mess_ifsuccess,
        'cate': cate,
        'content': one.dmess_content if cate=="代办" else one.mess_content,
        'wechat': per.user_wechat,
        'qq': per.user_qq,
        'phone': per.user_phone,
        'flag': 1 if request.COOKIES.get('name')==user else 0,
    })


#查看服务商库/需求大厅/代办中心
def allService(request,cate):
    # 猜你喜欢
    love_list = Message.objects.all().order_by('-mess_seenum')[:9]

    # cate
    if cate=="需求":
        title_name = "需求大厅"
        cate_list = Cate.objects.all().order_by('cate_num')
    elif cate=="服务":
        title_name = "服务商库"
        cate_list = Cate.objects.all().order_by('cate_num')
    else:
        title_name = "代办中心"
        cate_list = DCate.objects.all().order_by('dcate_num')
    # 分页
    if cate=="代办":
        mess_list = DMessage.objects.all().order_by("-dmess_time")
    else:
        mess_list = Message.objects.filter(mess_xuorfu=cate).order_by("-mess_time")
    paginator = Paginator(mess_list, 10)  # Show 20 contacts per page
    page = request.GET.get('page')
    try:
        all_mess = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        all_mess = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        all_mess = paginator.page(paginator.num_pages)

    return render_to_response('supmarket.html',{
        'user_name': request.COOKIES.get('name',''),
        "len_list": range(1, paginator.num_pages+1),
        "all_mess": all_mess,
        'title_name': title_name,
        'cate': cate,
        'cate_list': cate_list,
        'love_list': love_list,
    })

# 过滤条件筛选
@csrf_exempt
def searchmess(request,cate):
    if request.method=="POST":
        category = request.POST.get('category')
        price = request.POST.get('price')
        price_up_down = request.POST.get('price_up_down')
        date = request.POST.get('date')
        date_up_down = request.POST.get('date_up_down')
        oknum_up_down = request.POST.get('oknum_up_down')
        seenum_up_down = request.POST.get("seenum_up_down")
        # 猜你喜欢
        love_list = Message.objects.all().order_by('-mess_seenum')[:9]

        # cate
        if cate == "需求":
            title_name = "需求大厅"
            cate_list = Cate.objects.all().order_by('cate_num')
        elif cate == "服务":
            title_name = "服务商库"
            cate_list = Cate.objects.all().order_by('cate_num')
        else:
            title_name = "代办中心"
            cate_list = DCate.objects.all().order_by('dcate_num')

        # onecate 为小类别  cate 为 服务，需求，代办中的一个
        if cate == '代办':
            # category
            if category=='all':
                category_list=['生活缴费','代取快递','代取餐','代创意','代行动','代其他']
            else:
                category_list = [category]

            # price filter
            filter_price_start = float(price.split("-")[0])
            filter_price_end = float(price.split("-")[1])
            if price_up_down == "byself" or price_up_down=="price_up":
                sort_price = "dmess_price"
            else:
                sort_price = '-dmess_price'

            # filter date
            import datetime
            today_time = datetime.datetime.now()
            time_cha = datetime.timedelta(days=int(date))
            filter_start_time = today_time-time_cha

            if date_up_down == 'byself' or date_up_down=='date_up':
                sort_date = 'dmess_time'
            else:
                sort_date = '-dmess_time'

            # filter oknum
            if oknum_up_down == 'byself' or oknum_up_down == 'oknum_up':
                sort_oknum = 'dmess_compeletenum'
            else:
                sort_oknum = '-dmess_compeletenum'

            # filter seenum
            if seenum_up_down == 'byself' or seenum_up_down == 'seenum_up':
                sort_seenum = 'dmess_seenum'
            else:
                sort_seenum = '-dmess_seenum'

            mess_list = DMessage.objects.filter(dmess_cate__dcate_name__in=category_list,\
                                                dmess_price__range=[filter_price_start,filter_price_end],\
                                                dmess_time__gte=filter_start_time,
                                                ).order_by(sort_price)\
                                                 .order_by(sort_date)\
                                                 .order_by(sort_oknum)\
                                                 .order_by(sort_seenum)
        else:
            # category
            if category == 'all':
                category_list = ['美工设计', '文案策划', '运营推广', '网站建设', 'APP开发', '微信开发', '多媒体处理', '其他']
            else:
                category_list = [category]

            # price filter
            filter_price_start = float(price.split("-")[0])
            filter_price_end = float(price.split("-")[1])
            if price_up_down == "byself" or price_up_down == "price_up":
                sort_price = "mess_price"
            else:
                sort_price = '-mess_price'

            # filter date
            import datetime
            today_time = datetime.datetime.now()
            time_cha = datetime.timedelta(days=int(date))
            filter_start_time = today_time - time_cha

            if date_up_down == 'byself' or date_up_down == 'date_up':
                sort_date = 'mess_time'
            else:
                sort_date = '-mess_time'

            # filter oknum
            if oknum_up_down == 'byself' or oknum_up_down == 'oknum_up':
                sort_oknum = 'mess_compeletenum'
            else:
                sort_oknum = '-mess_compeletenum'

            # filter seenum
            if seenum_up_down == 'byself' or seenum_up_down == 'seenum_up':
                sort_seenum = 'mess_seenum'
            else:
                sort_seenum = '-mess_seenum'

            mess_list = Message.objects.filter(mess_cate__cate_name__in=category_list, \
                                                mess_price__range=[filter_price_start, filter_price_end], \
                                                mess_time__gte=filter_start_time,
                                                ).order_by(sort_price) \
                                                 .order_by(sort_date) \
                                                 .order_by(sort_oknum) \
                                                 .order_by(sort_seenum)
            # mess_list = Message.objects.filter(mess_cate__cate_name=category).order_by("-mess_time")

        return render_to_response('supmarket.html', {
            'user_name': request.COOKIES.get('name', ''),
            "all_mess": mess_list,
            'title_name': title_name,
            'cate': cate,
            'cate_list': cate_list,
            'love_list': love_list,
            'default_category': category,
            'default_price': price,
            'default_sort_price': price_up_down,
            'default_date': date,
            'default_sort_date': date_up_down,
            'default_sort_oknum': oknum_up_down,
            'default_sort_seenum': seenum_up_down,
        })


def Onecate(request,cate,onecate):
    # onecate 为小类别  cate 为 服务，需求，代办中的一个
    if cate=='代办':
        mess_list = DMessage.objects.filter(dmess_cate__dcate_name=onecate).order_by("-dmess_time")
        cate_list = DCate.objects.all().order_by('dcate_num')
    else:
        mess_list = Message.objects.filter(mess_cate__cate_name=onecate).order_by("-mess_time")
        cate_list = Cate.objects.all().order_by('cate_num')

    paginator = Paginator(mess_list, 10)  # Show 20 contacts per page
    page = request.GET.get('page')
    try:
        all_mess = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        all_mess = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        all_mess = paginator.page(paginator.num_pages)
    return render_to_response('supmarket.html',{
        'user_name': request.COOKIES.get('name',''),
        "len_list": range(1, paginator.num_pages + 1),
        "all_mess": all_mess,
        'cate': cate,
        'cate_list': cate_list,
        'title_name': onecate,
    })



# 搜索
@csrf_exempt
def search(request):
    if request.method=='POST':
        cate = request.POST.get('search_cate')[1:]
        content = request.POST.get('search_content')
        # Q查询保证 或 条件
        if cate=='代办':
            mess_list = DMessage.objects.filter(
                Q(dmess_title__contains=content)|Q(dmess_content__contains=content)
            )
        else:
            mess_list = Message.objects.filter(
                Q(mess_title__contains=content) | Q(mess_content__contains=content)
            )

        paginator = Paginator(mess_list, 10)  # Show 20 contacts per page
        page = request.GET.get('page')
        try:
            all_mess = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            all_mess = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            all_mess = paginator.page(paginator.num_pages)

        return render_to_response('search_result.html',{
            'cate': cate,
            'content': content,
            'user_name': request.COOKIES.get('name', ''),

            "len_list": range(1, paginator.num_pages + 1),
            "all_mess": all_mess,
        })
    else:
        return render_to_response('search_result.html',{
            'user_name': request.COOKIES.get('name', ''),
        })