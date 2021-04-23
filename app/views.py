from django.shortcuts import render,redirect
from django.views import View
from .models import Customer, Product, Cart, OrderPlaced
from .forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class HomeView(View):
	def get(self,request):
		total_item = 0

		topwears = Product.objects.filter(category='TW')
		bottomwears = Product.objects.filter(category='BW')
		mobiles = Product.objects.filter(category='M')
		if request.user.is_authenticated:
			total_item = len(Cart.objects.filter(user=request.user))
		context ={
		'topwears':topwears,
		'bottomwears':bottomwears,
		'mobiles':mobiles,
		'total_item':total_item
		}

		return render(request,'app/home.html',context)


class ProductDetailView(View):
	def get(self,request,pk):
		total_item=0
		product = Product.objects.get(pk=pk)
		item_already_in_cart=False
		if request.user.is_authenticated:
			item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
		if request.user.is_authenticated:
			total_item = len(Cart.objects.filter(user=request.user))
		context ={
			'product':product,
			'item_already_in_cart':item_already_in_cart,
			'total_item':total_item
		}
		return render(request,'app/productdetail.html',context)


@method_decorator(login_required,name='dispatch')
class ProfileView(View):
	def get(self,request):
		total_item=0
		if request.user.is_authenticated:
			total_item=len(Cart.objects.filter(user=request.user))
		form = CustomerProfileForm()
		context={'form':form,
				 'active':' btn-primary',
				 'total_item':total_item}
		return render(request,'app/profile.html',context)

	def post(self,request):
		form = CustomerProfileForm(request.POST)
		if form.is_valid():
			user=request.user
			name = form.cleaned_data['name']
			locality = form.cleaned_data['locality']
			city = form.cleaned_data['city']
			state = form.cleaned_data['state']
			zipcode = form.cleaned_data['zipcode']
			reg=Customer(user=user,name=name,locality=locality,city=city,state=state,zipcode=zipcode)
			reg.save()
			messages.success(request,f'Profile Update successfully')
		return render(request,'app/profile.html',{'form':form,'active':'btn btn-primary'})



@login_required
def add_to_cart(request):
	user = request.user
	product_id=request.GET.get('prod_id')
	product = Product.objects.get(id=product_id)
	Cart(user=user,product=product).save()
	return redirect('/cart')
	
@login_required
def show_cart(request):
	total_item=0
	if request.user.is_authenticated:
		total_item = len(Cart.objects.filter(user=request.user))
	if request.user.is_authenticated:
		user =request.user
		cart = Cart.objects.filter(user=user)
		amount=0.0
		shipping_amount = 70.0
		total_amount = 0.0
		cart_product=[p for p in Cart.objects.all() if p.user==request.user]
		if cart_product:
			for p in cart_product:
				temp_amount =(p.quantity*p.product.discounted_price)
				amount+=temp_amount
				totalamount=amount + shipping_amount
			return render(request, 'app/addtocart.html',{'carts':cart,'totalamount':totalamount,'amount':amount,'total_item':total_item})
		else:
			return render(request,'app/emptycard.html')


def buy_now(request):
 return render(request, 'app/buynow.html')

def plus_cart(request):
	if request.method=="GET":
		prod_id=request.GET['prod_id']
		c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user)) 
		c.quantity+=1
		c.save()
		amount=0.0
		shipping_amount=70.0
		cart_product=[p for p in Cart.objects.all() if p.user==request.	user]
		for p in cart_product:
			temp_amount=(p.quantity*p.product.discounted_price)
			amount+=temp_amount


		data ={
		'quantity':c.quantity,
		'amount':amount,
		'totalamount':amount+shipping_amount
		}
		return JsonResponse(data)
def minus_cart(request):
	if request.method=="GET":
		prod_id=request.GET['prod_id']
		c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user)) 
		c.quantity-=1
		c.save()
		amount=0.0
		shipping_amount=70.0
		cart_product=[p for p in Cart.objects.all() if p.user==request.	user]
		for p in cart_product:
			temp_amount=(p.quantity*p.product.discounted_price)
			amount+=temp_amount
	

		data ={
		'quantity':c.quantity,
		'amount':amount,
		'totalamount':amount+shipping_amount
		}
		return JsonResponse(data)


def remove_cart(request):
	if request.method=="GET":
		prod_id=request.GET['prod_id']
		c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user)) 
		c.delete()
		amount=0.0
		shipping_amount=70.0
		cart_product=[p for p in Cart.objects.all() if p.user==request.	user]
		for p in cart_product:
			temp_amount=(p.quantity*p.product.discounted_price)
			amount+=temp_amount
		data ={
		'amount':amount,
		'totalamount':amount+shipping_amount
		}
		return JsonResponse(data)
@login_required
def address(request):
	total_item=0
	if request.user.is_authenticated:
		total_item=len(Cart.objects.filter(user=request.user))
	add = Customer.objects.filter(user=request.user)
	context={"add":add,
			 "active":'btn-primary',
			 'total_item':total_item}
	return render(request, 'app/address.html',context)

@login_required
def orders(request):
	op = OrderPlaced.objects.filter(user=request.user)
	context={'order_placed':op}
	return render(request, 'app/orders.html',context)



def mobile(request,data=None):
	total_item=0
	if data==None:
		mobiles = Product.objects.filter(category='M')
	elif data=='Mi' or data=='LG':
		mobiles = Product.objects.filter(category='M').filter(brand=data)
	elif data=='below':
		mobiles = Product.objects.filter(category='M').filter(discounted_price__lt=10000)
	elif data=='above':
		mobiles = Product.objects.filter(category='M').filter(discounted_price__gt=10000)
	if request.user.is_authenticated:
		total_item  = len(Cart.objects.filter(user=request.user))
	context={
		'mobiles':mobiles,
		'total_item':total_item
	}
	return render(request,'app/mobile.html',context)

def laptop(request,data=None):
	total_item=0
	if data==None:
		laptops = Product.objects.filter(category='L')
	elif data=='Hp' or data=='Lenovo'or data=='DELL':
		laptops = Product.objects.filter(category='L').filter(brand=data)
	elif data=='below':
		laptops = Product.objects.filter(category='L').filter(discounted_price__lt=50000)
	elif data=='above':
		laptops = Product.objects.filter(category='L').filter(discounted_price__gt=50000)
	if request.user.is_authenticated:
		total_item  = len(Cart.objects.filter(user=request.user))
	context={
		'laptops':laptops,
		'total_item':total_item
	}
	return render(request,'app/laptop.html',context)

def topwear(request,data=None):
	total_item=0
	if data==None:
		topwears = Product.objects.filter(category='TW')
	elif data=='below':
		topwears = Product.objects.filter(category='TW').filter(discounted_price__lt=100)
	elif data=='above':
		topwears = Product.objects.filter(category='TW').filter(discounted_price__gt=100)
	if request.user.is_authenticated:
		total_item  = len(Cart.objects.filter(user=request.user))
	context={
		'topwears':topwears,
		'total_item':total_item
	}
	return render(request,'app/topwear.html',context)

def bottomwear(request,data=None):
	total_item=0
	if data==None:
		bottomwears = Product.objects.filter(category='BW')
	elif data=='below':
		bottomwears = Product.objects.filter(category='BW').filter(discounted_price__lt=100)
	elif data=='above':
		bottomwears = Product.objects.filter(category='BW').filter(discounted_price__gt=100)
	if request.user.is_authenticated:
		total_item  = len(Cart.objects.filter(user=request.user))
	context={
		'bottomwears':bottomwears,
		'total_item':total_item
	}
	return render(request,'app/bottomwear.html',context)



def login(request):
	return render(request, 'app/login.html')
def logout(request):
	return render(request, 'app/login.html')


def customerregistration(request):
	if request.method=="POST":
		form = CustomerRegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('login')
			
	else:
		form = CustomerRegistrationForm()
	context={
		'form':form
	}
	return render(request, 'app/customerregistration.html',context)

@login_required
def checkout(request):
	user =request.user
	add = Customer.objects.filter(user=user)
	cart_item = Cart.objects.filter(user=user)
	amount = 0.0
	shipping_amount=70.0
	totalamount=0.0
	cart_product=[p for p in Cart.objects.all() if p.user==request.	user]
	if cart_product:
		for p in cart_product:
			temp_amount=(p.quantity*p.product.discounted_price)
			amount+=temp_amount
		totalamount=amount+shipping_amount

	context={'add':add,
			 'totalamount':totalamount,
			 'cart_item':cart_item}
	return render(request, 'app/checkout.html',context)

@login_required
def payment_done(request):
	user = request.user
	custid = request.GET.get('custid')
	customer = Customer.objects.get(id=custid)
	cart = Cart.objects.filter(user=user)
	for c in cart:
		OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity).save()
		c.delete()
	return redirect('orders')