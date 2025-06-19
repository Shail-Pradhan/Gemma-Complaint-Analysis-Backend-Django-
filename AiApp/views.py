from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId
import json
from datetime import datetime
from .db import complaints_collection

@csrf_exempt
def complaint_list(request):
    """Handle GET requests to list all complaints"""
    if request.method == 'GET':
        try:
            complaints = list(complaints_collection.find())
            # Convert ObjectId to string for JSON serialization
            for complaint in complaints:
                complaint['_id'] = str(complaint['_id'])
            return JsonResponse({'complaints': complaints})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def complaint_create(request):
    """Handle POST requests to create a new complaint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Add timestamp
            data['time'] = datetime.now().strftime('%H:%M')
            data['date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Validate required fields
            required_fields = ['profile_name', 'complaint_query']
            if not all(field in data for field in required_fields):
                return JsonResponse({'error': 'Missing required fields'}, status=400)
            
            result = complaints_collection.insert_one(data)
            return JsonResponse({
                'message': 'Complaint created successfully',
                'id': str(result.inserted_id)
            }, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def complaint_detail(request, complaint_id):
    """Handle GET requests for a specific complaint"""
    if request.method == 'GET':
        try:
            complaint = complaints_collection.find_one({'_id': ObjectId(complaint_id)})
            if complaint:
                complaint['_id'] = str(complaint['_id'])
                return JsonResponse(complaint)
            return JsonResponse({'error': 'Complaint not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def complaint_update(request, complaint_id):
    """Handle PUT requests to update a complaint"""
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            result = complaints_collection.update_one(
                {'_id': ObjectId(complaint_id)},
                {'$set': data}
            )
            if result.modified_count:
                return JsonResponse({'message': 'Complaint updated successfully'})
            return JsonResponse({'error': 'Complaint not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def complaint_delete(request, complaint_id):
    """Handle DELETE requests to remove a complaint"""
    if request.method == 'DELETE':
        try:
            result = complaints_collection.delete_one({'_id': ObjectId(complaint_id)})
            if result.deleted_count:
                return JsonResponse({'message': 'Complaint deleted successfully'})
            return JsonResponse({'error': 'Complaint not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)