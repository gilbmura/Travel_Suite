#!/usr/bin/env python3
"""
Comprehensive API testing script for TravelSuite
Tests all endpoints to verify the system is working correctly
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://127.0.0.1:8000/api'
ACCESS_TOKEN = None

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'


def print_test(message):
    print(f'{CYAN}[TEST]{RESET} {message}')


def print_success(message):
    print(f'{GREEN}✓ {message}{RESET}')


def print_error(message):
    print(f'{RED}✗ {message}{RESET}')


def print_info(message):
    print(f'{YELLOW}ℹ {message}{RESET}')


def test_api_root():
    """Test API root endpoint"""
    print_test('Testing API root endpoint')
    try:
        response = requests.get(f'{BASE_URL}/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f'API root reachable: {data}')
            return True
        else:
            print_error(f'API root returned {response.status_code}')
            return False
    except Exception as e:
        print_error(f'API root failed: {e}')
        return False


def test_admin_login():
    """Test admin login"""
    global ACCESS_TOKEN
    print_test('Testing admin login')
    try:
        response = requests.post(
            f'{BASE_URL}/auth/login/',
            json={'username': 'admin', 'password': 'Admin@123'},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            ACCESS_TOKEN = data.get('access')
            print_success(
                f'Admin login successful, token: {ACCESS_TOKEN[:20]}...')
            return True
        else:
            print_error(
                f'Admin login failed: {response.status_code} - {response.text}')
            return False
    except Exception as e:
        print_error(f'Admin login error: {e}')
        return False


def test_routes_list():
    """Test listing routes"""
    print_test('Testing list routes')
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'} if ACCESS_TOKEN else {}
    try:
        response = requests.get(
            f'{BASE_URL}/routes/', headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('results', data)) if isinstance(
                data, dict) else len(data)
            print_success(f'Routes listed: {count} routes found')
            return True
        else:
            print_error(f'Routes list failed: {response.status_code}')
            return False
    except Exception as e:
        print_error(f'Routes list error: {e}')
        return False


def test_vehicles_list():
    """Test listing vehicles"""
    print_test('Testing list vehicles')
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'} if ACCESS_TOKEN else {}
    try:
        response = requests.get(
            f'{BASE_URL}/vehicles/', headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('results', data)) if isinstance(
                data, dict) else len(data)
            print_success(f'Vehicles listed: {count} vehicles found')
            return True
        else:
            print_error(f'Vehicles list failed: {response.status_code}')
            return False
    except Exception as e:
        print_error(f'Vehicles list error: {e}')
        return False


def test_customers_list():
    """Test listing customers"""
    print_test('Testing list customers')
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'} if ACCESS_TOKEN else {}
    try:
        response = requests.get(
            f'{BASE_URL}/customers/', headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('results', data)) if isinstance(
                data, dict) else len(data)
            print_success(f'Customers listed: {count} customers found')
            return True
        else:
            print_error(f'Customers list failed: {response.status_code}')
            return False
    except Exception as e:
        print_error(f'Customers list error: {e}')
        return False


def test_bookings_list():
    """Test listing bookings"""
    print_test('Testing list bookings')
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'} if ACCESS_TOKEN else {}
    try:
        response = requests.get(
            f'{BASE_URL}/bookings/', headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('results', data)) if isinstance(
                data, dict) else len(data)
            print_success(f'Bookings listed: {count} bookings found')
            return True
        else:
            print_error(f'Bookings list failed: {response.status_code}')
            return False
    except Exception as e:
        print_error(f'Bookings list error: {e}')
        return False


def test_admin_page():
    """Test admin dashboard page"""
    print_test('Testing admin dashboard page')
    try:
        response = requests.get('http://127.0.0.1:8000/admin/', timeout=5)
        if response.status_code == 200:
            print_success('Admin dashboard accessible')
            return True
        else:
            print_error(f'Admin dashboard returned {response.status_code}')
            return False
    except Exception as e:
        print_error(f'Admin dashboard error: {e}')
        return False


def run_all_tests():
    """Run all tests"""
    print(f'\n{CYAN}╔════════════════════════════════════════════╗{RESET}')
    print(f'{CYAN}║  TravelSuite API Comprehensive Test Suite  ║{RESET}')
    print(f'{CYAN}╚════════════════════════════════════════════╝{RESET}\n')

    tests = [
        ('API Root', test_api_root),
        ('Admin Login', test_admin_login),
        ('List Routes', test_routes_list),
        ('List Vehicles', test_vehicles_list),
        ('List Customers', test_customers_list),
        ('List Bookings', test_bookings_list),
        ('Admin Dashboard', test_admin_page),
    ]

    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
        print()

    print(f'{CYAN}╔════════════════════════════════════════════╗{RESET}')
    print(f'{CYAN}║  Test Summary                              ║{RESET}')
    print(f'{CYAN}╚════════════════════════════════════════════╝{RESET}\n')

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f'{GREEN}PASS{RESET}' if result else f'{RED}FAIL{RESET}'
        print(f'  {status} {test_name}')

    print(f'\n{YELLOW}Total: {passed}/{total} tests passed{RESET}\n')

    if passed == total:
        print(f'{GREEN}All tests passed! ✓{RESET}\n')
    else:
        print(f'{RED}Some tests failed. Check the output above.{RESET}\n')


if __name__ == '__main__':
    run_all_tests()
