from django.shortcuts import render
from django.http import HttpResponse,Http404
from django.shortcuts import redirect, get_object_or_404
from django.forms import ModelForm
from .models import Item,UserProfile,ConfirmString,Comment,Likes
import datetime,pytz
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import auth
from django.db.models import *
from .forms import RegisterForm, LoginForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
import operator

import hashlib


class ItemForm(ModelForm):
     class Meta:
         model = Item
         fields = [ 'name', 'price', 'condition','keyword','category', 'description', 'picture', 'userid']

class CommentForm(ModelForm):
     class Meta:
         model = Comment
         fields = ['itemid', 'buyername', 'buyeremail', 'buyerphone', 'commenttext']#, 'commentdate']

def home(request):
    items = Item.objects.all()
    if request.session.get('is_login',None):
         return render(request, 'profile.html',{'items': items})
    else:
         return render(request, 'home.html',{'items': items})

def item_create(request):
     if request.POST:
        temp = request.POST.copy()
        temp['userid'] = request.session.get('user_id', None)
        form = ItemForm(temp, request.FILES)
     else:
        form = ItemForm(None)
     if form.is_valid():
        form.save()
        return redirect('profile')
     return render(request, 'add_item.html', {'form':form})
    # s_name = request.POST.get('name', None)
    # s_itemid = request.POST.get('itemid',None)
    # s_condition = request.POST.get('condition', None)
    # s_price = request.POST.get('price', None)
    # s_description = request.POST.get('description',None)
    # s_picture = request.POST.get('picture',None)
    #
    # if s_name and s_description and s_price and s_condition and s_itemid:
    #     newitem = Item()
    #     newitem.name = s_name
    #     newitem.itemid = s_itemid
    #     newitem.condition = s_condition
    #     newitem.price = s_price
    #     newitem.description = s_description
    #     newitem.picture = s_picture
    #     newitem.save()
    #     return redirect('home')
def item_detail(request, id, template_name='item_detail.html'):
    item = get_object_or_404(Item, itemid=id)
    seller = UserProfile.objects.get(userid = item.userid)
    userid = request.session.get('user_id', None)
    try:
        liked = Likes.objects.get(itemid=id, userid = userid)
    except Likes.DoesNotExist:
        liked = None

    bool_liked = False
    if liked:
        bool_liked = True

    comment_exist = True
    if request.POST:
        temp = request.POST.copy()
        temp['itemid'] = id
        temp['buyername'] = request.session.get('user_name', None)
        temp['buyeremail'] = request.session.get('user_email', None)
        temp['buyerphone'] = request.session.get('user_phone', None)
        form = CommentForm(temp)
    else:
        form = ItemForm(None)

    try:
        comments = Comment.objects.filter(itemid=id)
    except Comment.DoesNotExist:
        comment_exist = False

    if form.is_valid():
       post = form.save(commit=False)
       post.save()
       form = ItemForm(None)
       request.POST = None
       comments = Comment.objects.filter(itemid=id)
       return render(request, 'redirect.html', {'item':item, 'seller':seller, 'description': item.description, 'comments': comments})

    if comment_exist:
        return render(request, template_name, {'item':item, 'seller':seller, 'description': item.description, 'comments': comments, 'bool_liked': bool_liked})
    else:
        return render(request, template_name, {'item':item, 'seller':seller, 'description': item.description, 'bool_liked': bool_liked})#, 'comments': comments})

def item_update(request, id, template_name='update_item.html'):
    item = get_object_or_404(Item, itemid=id)
    form = ItemForm(request.POST or None, instance=item)

    if request.POST:
        temp = request.POST.copy()
        temp['userid'] = request.session.get('user_id', None)
        form = ItemForm(temp)
    else:
        form = ItemForm(None)

    if form.is_valid():
        oldid = item.itemid
        item.delete()
        f = form.save(commit=False)
        f.itemid = oldid
        f.save()
        return redirect('MyItems')
    return render(request, template_name, {'item':item, 'description': item.description})


def item_delete(request, id, template_name='home.html'):
    item = get_object_or_404(Item, itemid=id)

    item.delete()
    return redirect('profile')

def item_search(request, template_name='search_item.html'):
    if request.method == 'POST':
        name = request.POST.get('name', None)


        lprice = request.POST.get('lprice', None)
        hprice = request.POST.get('hprice', None)

        s_condition = request.POST.get('condition', None)
        s_category = request.POST.get('category', None)
        res = Item.objects.all()

        if name:
            res = res.filter(name__icontains = name)

        if lprice or hprice:
            if lprice:
                res = res.filter(price__gte = float(lprice))
            if hprice:
                res = res.filter(price__lte = float(hprice))

        if s_condition:
            res = res.filter(condition = s_condition)

        if s_category:
            res = res.filter(category = s_category)

        data = {}
        data['item_list'] = res
        return render(request, 'search_result.html', data)

    return render(request, template_name)



def login(request):
    if request.session.get('is_login',None):
        return redirect("home")
    if request.method == 'POST':
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
        try:
            user = UserProfile.objects.get(username=username)
            if not user.has_confirmed:
                message = "Please Verify Your Email Address!"
                return render(request, 'login/login.html',locals())
            if user.password == password:
                request.session['is_login'] = True
                request.session['user_id'] = str(user.userid)
                request.session['user_name'] = user.username
                request.session['user_phone'] = user.phonenumber
                request.session['user_email'] = user.email
                return redirect('profile')
            else:
                message = "Wrong Password!"
        except:
            message = "User does not exist"
        return render(request, 'login/login.html', {"message" : message},locals())
    return render(request, 'login/login.html',locals())
    #         user = auth.authenticate(username = username, password = password1)
    #         if user is not None and user.is_active:
    #             auth.login(request, user)
    #             return HttpResponseRedirect(reverse('profile', arg=[user.id]))
    #     else:
    #         return render(request, 'login/login.html', {'form':form, 'message': 'Wrong password. Please try again.'})
    #
    # else:
    #     form = LoginForm()
    # return render(request, 'login/login.html', {'form': form})

# def login(request):
#     if request.method == "POST":
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         print(username, password)
#         return redirect('/index/')
#     return render(request, 'login/login.html')



def register(request):
    if request.session.get('is_login', None):
        return redirect("/home/")
    if request.method == 'POST':
        register_form = RegisterForm(request.POST)
        message = "Please Check your information!"
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            email = register_form.cleaned_data['email']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            phonenumber = register_form.cleaned_data['phonenumber']
            address = register_form.cleaned_data['address']

            if password1 != password2:  #Password Check if the same
                message = "Please check your password!"
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = UserProfile.objects.filter(username=username)
                if same_name_user:  #Unique Username
                    message = 'User Already Exist, Please choose another Username'
                    return render(request, 'login/register.html', locals())
                same_email_user = UserProfile.objects.filter(email=email)
                if same_email_user:
                    message = 'Email address already registered, please register with another email.'
                    return render(request, 'login/register.html', locals())

                new_user = UserProfile()
                new_user.username = username
                new_user.password = password1
                new_user.email = email
                new_user.phonenumber = phonenumber
                new_user.address = address
                new_user.save()


                code = make_confirm_string(new_user)
                send_email(email,code)

                message = "Please check your email inbox and confirm your email address."
            # user = UserProfile.objects.create_user(username=username, password=password1, email=email)
            # user_profile = UserProfile(user=username)
            # user_profile.address = address
            # user_profile.phonenumber = phonenumber
            # user_profile.save()

            return redirect('/login/login.html',locals())
    register_form = RegisterForm()
    return render(request, 'login/register.html', locals())
    #
    #

    #         #return HttpResponseRedirect("../login/login.html")
    #         return render(request, 'login/login.html')
    # else:
    #     form = RegisterForm()
    #
    # return render(request, 'login/register.html', {'form': form})

#    return render(request, 'login/register.html')
def hash_code(s, salt='mysite'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()

def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.username, now)
    ConfirmString.objects.create(code=code, user=user)
    return code

def send_email(email, code):

    from django.core.mail import EmailMultiAlternatives
    print("send_email:" + code)
    subject = 'Confirmation Email from IlliniFleaMarket'

    text_content = '''Thank you for registering at IlliniFleaMarket, where Fighting Illini Trades.\
                    If you are seeing this message, this email is not displaying HTML content correctly, Please
                    contact your email service provider.'''
    print("send_email:" + code)
    html_content = '''
                    <p>Thank you for registering at IlliniFleaMarket, <a href="{}/confirm/?code={}" target=blank>www.illinifleamarket.com</a>，\
                    where Fighting Illini Trades.</p>
                    <p>Please click on the link to verify your email address.</p>
                    <p>This link will expire in {} days.</p>
                    '''.format('http://illinifleamarket.com', code, settings.CONFIRM_DAYS)
    print("send_email:" + code)
    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def user_confirm(request):
    code = request.GET.get('code', None)
    message = ''
    try:
        confirm = ConfirmString.objects.get(code=code)
    except:
        message = 'Invaid Verification Request!'
        return render(request, 'login/confirm.html', locals())

    c_time = confirm.c_time
    now = datetime.datetime.now()
    now=now.replace(tzinfo=pytz.timezone('UTC'))
    print(now.tzinfo==None)
    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = 'The link you used has expired, Please register again.'
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = 'Thank you for verifying your email, please Login.'
        return render(request, 'login/confirm.html', locals())

def like(request, id):

    userid=request.session.get('user_id', None)
    like = Likes(userid=userid, itemid=id)

    like.save()

    #context = {'itemid' : id}
    return redirect("item_detail", id)
    #return render(request, 'like.html', context)

def dislike(request, id):

    userid=request.session.get('user_id', None)
    like = Likes.objects.get(userid=userid, itemid=id)
    like.delete()

    #context = {'itemid' : id}
    #return render(request, 'item_detail.html', context)
    return redirect("item_detail", id)

def recommendation(request):
    temp = []
    userid = request.session.get('user_id', None)
    items = Likes.objects.filter(userid=userid).order_by('-id')[:3]

    for item_like in items:
        itemid_first = item_like.itemid
        print("itemid_first is")
        print(itemid_first)
        item = Item.objects.get(itemid=itemid_first)
        keyword = item.keyword
        price = item.price
        category = item.category
        condition = item.condition

        m = Item.objects.filter(category=category).filter(keyword=keyword).exclude(userid=userid)
        print("here m")
        print(m)
        totalNumber = m.count()


        weights = {}

        for item in m:
            weight = measurePrice(item.price) + measureCondition(item.condition)
            itemid = item.itemid
            weights[itemid] = weight
        weight_sorted = sorted(weights.items(), key=operator.itemgetter(1))
        weight_sorted.reverse()
        print("here weight_sorted")
        print(weight_sorted)
        recomItems = []
        if totalNumber >= 5:
            recomItems = weight_sorted[:5]
        else:
            recomItems = weight_sorted
            print("here recomItems")
            print(recomItems)
            n = Item.objects.filter(category=category).exclude(keyword__exact=keyword).exclude(userid = userid)
            print("here n")
            print(n)
            weights_category = {}
            for item in n:
                weight = measurePrice(item.price) + measureCondition(item.condition)
                itemid = item.itemid
                weights_category[itemid] = weight
            weight_sorted_category = sorted(weights_category.items(), key=operator.itemgetter(1))
            weight_sorted_category.reverse()
            number = n.count()
            if number > 5 - totalNumber:
                a = 5 - totalNumber
                for i in range(a):
                    recomItems.append(weight_sorted_category[i])
            else:
                for i in range(number):
                    recomItems.append(weight_sorted_category[i])


            for j in recomItems:
                if j[0] in temp:
                    pass
                else:
                    temp.append(j[0])
            print("here's temp")
            print(temp)

    recom = []
    for i in range(len(temp)):
        item = Item.objects.get(itemid=temp[i])
        recom.append(item)

    context = {'items' : recom}
    return render(request, 'recommendation.html', context)

def measurePrice(price):
    if price < 20:
        weight = 5
    elif price < 50:
        weight = 4
    elif price < 100:
        weight = 3
    elif price < 1000:
        weight = 2
    else:
        weight = 1
    return weight

def measureCondition(condition):
    if condition == "BrandNew":
        weight = 3
    elif condition == "New(Other)":
        weight = 2
    else:
        weight = 1
    return weight


def logout(request):
    if not request.session.get('is_login', None):
        return redirect("home")
    request.session.flush()
    return redirect("home")

def profile(request):
    items = Item.objects.all()
    return render(request, 'profile.html',{'items': items})

def MyItems(request):
    this_user_id = request.session.get('user_id', None)
    items = Item.objects.filter(userid = this_user_id)
    return render(request, 'MyItems.html',{'items': items})

def profile_update(request):
    pass

def pwd_change(request):
    pass
'''
    def book_search(request,template_name='books_fbv/book_search.html'):
    #form = BookForm(request.POST or None, instance=book)
    if request.method == 'POST':
        lPage = request.POST.get('lPage', None)
        hPage = request.POST.get('hPage', None)
        books = Book.objects.filter(pages__range=(int(lPage), int(hPage)))
        data = {}
        data['object_list'] = books
        #hp = request.POST.get('page', None)
        #return redirect('books_fbv:book_list')
        print(data)
        return render(request, 'books_fbv/book_searchRes.html', data)
    return render(request, template_name, {'a':a})

def book_search_Res(request,template_name='books_fbv/book_search.html'):
    a = 10
    #form = BookForm(request.POST or None, instance=book)
    if request.method == POST:

        #lp = request.POST.get('page', None)
        #hp = request.POST.get('page', None)
        #return redirect('books_fbv:book_list')
        print(request.POST)
        render(request, 'books_fbv/book_searchRes.html', {'form':form})
    return render(request, template_name, {'a':a})
'''
