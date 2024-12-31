from django.shortcuts import render


def index(request):
	return render(request, 'stock_track/index.html')
