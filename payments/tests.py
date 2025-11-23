from django.test import TestCase
from django.conf import settings
from payments.mtn_adapter import MTNAdapter
from payments.airtel_adapter import AirtelAdapter


class PaymentAdapterTest(TestCase):
    """Test payment adapters in mock mode."""
    
    def setUp(self):
        # Ensure mock mode
        settings.PAYMENTS_MODE = 'mock'
    
    def test_mtn_create_payment(self):
        """Test MTN payment creation."""
        result = MTNAdapter.create_payment(
            phone_number="+250788123456",
            amount=5000
        )
        
        self.assertTrue(result['success'])
        self.assertIn('transaction_id', result)
        self.assertEqual(result['status'], 'pending')
    
    def test_mtn_verify_payment(self):
        """Test MTN payment verification."""
        create_result = MTNAdapter.create_payment(
            phone_number="+250788123456",
            amount=5000
        )
        
        verify_result = MTNAdapter.verify_payment(create_result['transaction_id'])
        
        self.assertTrue(verify_result['success'])
        self.assertEqual(verify_result['status'], 'completed')
    
    def test_mtn_refund_payment(self):
        """Test MTN refund."""
        create_result = MTNAdapter.create_payment(
            phone_number="+250788123456",
            amount=5000
        )
        
        refund_result = MTNAdapter.refund_payment(
            transaction_id=create_result['transaction_id'],
            amount=5000
        )
        
        self.assertTrue(refund_result['success'])
        self.assertIn('refund_id', refund_result)
        self.assertEqual(refund_result['status'], 'completed')
    
    def test_airtel_create_payment(self):
        """Test Airtel payment creation."""
        result = AirtelAdapter.create_payment(
            phone_number="+250788123456",
            amount=5000
        )
        
        self.assertTrue(result['success'])
        self.assertIn('transaction_id', result)
        self.assertEqual(result['status'], 'pending')
    
    def test_airtel_verify_payment(self):
        """Test Airtel payment verification."""
        create_result = AirtelAdapter.create_payment(
            phone_number="+250788123456",
            amount=5000
        )
        
        verify_result = AirtelAdapter.verify_payment(create_result['transaction_id'])
        
        self.assertTrue(verify_result['success'])
        self.assertEqual(verify_result['status'], 'completed')
    
    def test_airtel_refund_payment(self):
        """Test Airtel refund."""
        create_result = AirtelAdapter.create_payment(
            phone_number="+250788123456",
            amount=5000
        )
        
        refund_result = AirtelAdapter.refund_payment(
            transaction_id=create_result['transaction_id'],
            amount=5000
        )
        
        self.assertTrue(refund_result['success'])
        self.assertIn('refund_id', refund_result)
        self.assertEqual(refund_result['status'], 'completed')

