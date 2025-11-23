"""
MTN Mobile Money payment adapter.
In MVP, this is mocked. Replace with actual MTN API calls for production.
"""
import time
import uuid
from decimal import Decimal
from django.conf import settings


class MTNAdapter:
    """MTN Mobile Money payment adapter."""
    
    @staticmethod
    def create_payment(phone_number, amount, transaction_id=None, idempotency_key=None):
        """
        Create a payment request.
        
        Args:
            phone_number: Customer phone number
            amount: Payment amount
            transaction_id: Optional transaction ID
            idempotency_key: Optional idempotency key for duplicate prevention
            
        Returns:
            dict: {
                'success': bool,
                'transaction_id': str,
                'status': str,
                'message': str,
                'response_raw': dict
            }
        """
        if settings.PAYMENTS_MODE == 'mock':
            # Mock implementation
            time.sleep(0.5)  # Simulate API delay
            
            mock_transaction_id = transaction_id or f"MTN_{uuid.uuid4().hex[:16].upper()}"
            
            return {
                'success': True,
                'transaction_id': mock_transaction_id,
                'status': 'pending',
                'message': 'Payment request created successfully',
                'response_raw': {
                    'provider': 'mtn',
                    'transaction_id': mock_transaction_id,
                    'phone_number': phone_number,
                    'amount': str(amount),
                    'status': 'pending',
                    'timestamp': time.time(),
                }
            }
        else:
            # TODO: Replace with actual MTN API call
            # Example structure:
            # import requests
            # response = requests.post(
            #     'https://api.mtn.com/v1/payments',
            #     headers={'Authorization': f'Bearer {MTN_API_KEY}'},
            #     json={'phone': phone_number, 'amount': amount, ...}
            # )
            # return parse_response(response)
            raise NotImplementedError("MTN live payment integration not implemented. Set PAYMENTS_MODE=mock for MVP.")
    
    @staticmethod
    def verify_payment(transaction_id):
        """
        Verify payment status.
        
        Args:
            transaction_id: MTN transaction ID
            
        Returns:
            dict: {
                'success': bool,
                'status': str ('pending'|'completed'|'failed'),
                'message': str,
                'response_raw': dict
            }
        """
        if settings.PAYMENTS_MODE == 'mock':
            # Mock implementation - simulate verification
            time.sleep(0.3)
            
            # In mock mode, assume payment completes after verification
            return {
                'success': True,
                'status': 'completed',
                'message': 'Payment verified successfully',
                'response_raw': {
                    'provider': 'mtn',
                    'transaction_id': transaction_id,
                    'status': 'completed',
                    'timestamp': time.time(),
                }
            }
        else:
            # TODO: Replace with actual MTN API verification call
            raise NotImplementedError("MTN live payment verification not implemented. Set PAYMENTS_MODE=mock for MVP.")
    
    @staticmethod
    def refund_payment(transaction_id, amount, refund_id=None):
        """
        Refund a payment.
        
        Args:
            transaction_id: Original MTN transaction ID
            amount: Refund amount
            refund_id: Optional refund ID
            
        Returns:
            dict: {
                'success': bool,
                'refund_id': str,
                'status': str,
                'message': str,
                'response_raw': dict
            }
        """
        if settings.PAYMENTS_MODE == 'mock':
            # Mock implementation
            time.sleep(0.5)
            
            mock_refund_id = refund_id or f"MTN_REFUND_{uuid.uuid4().hex[:16].upper()}"
            
            return {
                'success': True,
                'refund_id': mock_refund_id,
                'status': 'completed',
                'message': 'Refund processed successfully',
                'response_raw': {
                    'provider': 'mtn',
                    'original_transaction_id': transaction_id,
                    'refund_id': mock_refund_id,
                    'amount': str(amount),
                    'status': 'completed',
                    'timestamp': time.time(),
                }
            }
        else:
            # TODO: Replace with actual MTN API refund call
            raise NotImplementedError("MTN live refund not implemented. Set PAYMENTS_MODE=mock for MVP.")

