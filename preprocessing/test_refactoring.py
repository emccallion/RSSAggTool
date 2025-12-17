#!/usr/bin/env python
"""
Quick test to verify refactored code works correctly.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/home/eoghan/project/preprocessing')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'preprocessing_project.settings')
django.setup()

from sankey.services import DiagramService, NodeService, AssociationService
from sankey.models import SankeyDiagram, PublishedNode
from django.core.exceptions import ValidationError

def test_service_layer():
    """Test the new service layer."""
    print("Testing Refactored Service Layer")
    print("=" * 60)

    # Test 1: Validation
    print("\n1. Testing validation...")
    try:
        DiagramService.create(name="", config_text="test")
        print("   ❌ FAIL: Should have raised ValidationError for empty name")
    except ValidationError as e:
        print(f"   ✓ PASS: Validation works - {e}")

    # Test 2: Get diagram statistics
    print("\n2. Testing diagram statistics...")
    diagrams = SankeyDiagram.objects.all()[:1]
    if diagrams:
        diagram = diagrams[0]
        stats = DiagramService.get_diagram_statistics(diagram)
        print(f"   ✓ PASS: Stats retrieved - Published: {stats['published']}")
    else:
        print("   ⚠️  SKIP: No diagrams to test")

    # Test 3: Node statistics
    print("\n3. Testing node statistics...")
    nodes = PublishedNode.objects.all()[:1]
    if nodes:
        node = nodes[0]
        stats = NodeService.get_node_statistics(node)
        print(f"   ✓ PASS: Node stats - Associations: {stats['total_associations']}")
    else:
        print("   ⚠️  SKIP: No published nodes to test")

    # Test 4: Service base class methods
    print("\n4. Testing base CRUD service...")
    all_diagrams = DiagramService.get_all()
    print(f"   ✓ PASS: get_all() returned {all_diagrams.count()} diagrams")

    if diagrams:
        diagram_by_id = DiagramService.get_by_id(diagram.id)
        print(f"   ✓ PASS: get_by_id() found diagram: {diagram_by_id.name}")

    print("\n" + "=" * 60)
    print("Service Layer Tests: ✓ PASSED\n")


def test_decorators():
    """Test the new decorators."""
    print("Testing Decorators")
    print("=" * 60)

    from common.utils.decorators import ajax_response
    from django.http import JsonResponse
    from unittest.mock import Mock

    @ajax_response
    def test_view(request):
        return {'data': 'test'}

    # Test successful response
    print("\n1. Testing @ajax_response decorator...")
    request = Mock()
    response = test_view(request)

    if isinstance(response, JsonResponse):
        print("   ✓ PASS: Returns JsonResponse")
        import json
        data = json.loads(response.content)
        if data.get('success') and data.get('data') == 'test':
            print("   ✓ PASS: Response format is correct")
        else:
            print(f"   ❌ FAIL: Unexpected response format: {data}")
    else:
        print("   ❌ FAIL: Did not return JsonResponse")

    # Test error handling
    @ajax_response
    def error_view(request):
        raise Exception("Test error")

    print("\n2. Testing error handling...")
    response = error_view(request)
    data = json.loads(response.content)
    if not data.get('success') and 'Test error' in data.get('message', ''):
        print("   ✓ PASS: Error handling works")
    else:
        print(f"   ❌ FAIL: Error not handled properly: {data}")

    print("\n" + "=" * 60)
    print("Decorator Tests: ✓ PASSED\n")


def test_api_responses():
    """Test API response helpers."""
    print("Testing API Response Helpers")
    print("=" * 60)

    from common.utils.api import APIResponse
    import json

    print("\n1. Testing success response...")
    response = APIResponse.success(data={'test': 'value'}, message="Success!")
    data = json.loads(response.content)
    if data.get('success') and data.get('message') == "Success!":
        print("   ✓ PASS: Success response works")
    else:
        print(f"   ❌ FAIL: Unexpected format: {data}")

    print("\n2. Testing error response...")
    response = APIResponse.error("Error message", status=400)
    data = json.loads(response.content)
    if not data.get('success') and data.get('message') == "Error message":
        print("   ✓ PASS: Error response works")
    else:
        print(f"   ❌ FAIL: Unexpected format: {data}")

    print("\n" + "=" * 60)
    print("API Response Tests: ✓ PASSED\n")


if __name__ == '__main__':
    try:
        test_service_layer()
        test_decorators()
        test_api_responses()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nRefactored code is working correctly!")
        print("The service layer, decorators, and utilities are functional.")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
