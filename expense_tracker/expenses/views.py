from django.shortcuts import render, redirect
from .models import Expense
from django.http import JsonResponse
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def expense_list(request):
    expenses = Expense.objects.all()
    return render(request, 'expenses/expense_list.html', {'expenses': expenses})

def add_expense(request):
    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        category = categorize_expense(description)
        Expense.objects.create(amount=amount, description=description, category=category)
        
        # Call LLM for analysis
        analysis = get_analysis(amount, category)
        return JsonResponse({'message': 'Expense added', 'analysis': analysis})
    return render(request, 'expenses/add_expense.html')

def categorize_expense(description):
    categories = {
        'Shopping': ['Flipkart', 'Amazon', 'Myntra'],
        'Food': ['Zomato', 'Swiggy'],
    }
    for category, keywords in categories.items():
        if any(keyword in description for keyword in keywords):
            return category
    return 'Others'

def get_analysis(amount, category):
    llm_api_url = os.getenv("LLM_API_URL")
    llm_api_key = os.getenv("LLM_API_KEY")
    headers = {'Authorization': f'Bearer {llm_api_key}'}
    data = {'prompt': f'Analyze the spending habits for {amount} on {category}.', 'max_tokens': 50}

    response = requests.post(llm_api_url, headers=headers, json=data)
    return response.json()['choices'][0]['text']
