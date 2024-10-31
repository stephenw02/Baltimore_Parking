from django.shortcuts import render
from django.http import HttpResponse
import json

# Create your views here.

def say_hello(request):
    return render(request, 'hello.html', { 'name': 'Raquel' })

def tickets_heatmap(request):
    return render(request, 'ticket_heatmap.html')

def tickets_plotmap(request):
    return render(request, 'ticket_plotmap.html')

def tickets_roadmap(request):
    return render(request, 'ticket_roadmap.html')

def towings_heatmap(request):
    return render(request, 'towing_heatmap.html')

def towings_plotmap(request):
    return render(request, 'towing_plotmap.html')

def towings_roadmap(request):
    return render(request, 'towing_roadmap.html')

def extras_view(request):
    with open("maps/templates/day_of_week.json") as f1, open("maps/templates/month.json") as f2, open("maps/templates/hour.json") as f3, open("maps/templates/car.json") as f4:
        week_data = json.load(f1)
        month_data = json.load(f2)
        hour_data = json.load(f3)
        car_data = json.load(f4)
    # Pass the data to the template
    week_json = json.dumps(week_data)  # Proper serialization
    month_json = json.dumps(month_data)
    hour_json = json.dumps(hour_data)
    car_json = json.dumps(car_data)
    return render(request, 'extras.html', {'week_json': week_json, 'month_json': month_json, 'hour_json': hour_json, 'car_json': car_json})

