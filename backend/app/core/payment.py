import httpx
import os
from typing import Dict, Any

async def verify_paystack_payment(reference: str, country_config: Dict[str, Any], expected_amount: float = None) -> Dict[str, Any]:
    """Verify Paystack payment on the backend"""
    try:
        # Get country-specific Paystack secret key
        country_name = country_config["name"].upper()
        secret_key = os.getenv(f'PAYSTACK_SECRET_KEY_{country_name}')
        
        # Fallback to default key if country-specific key is not found
        if not secret_key:
            secret_key = os.getenv('PAYSTACK_SECRET_KEY')
            print(f"Warning: Using default Paystack key. No specific key for {country_name}")
        
        if not secret_key:
            return {
                'success': False,
                'message': 'Paystack secret key not configured'
            }

        print(f"Verifying payment reference: {reference}")
        
        # Make request to Paystack
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'https://api.paystack.co/transaction/verify/{reference}',
                headers={
                    'Authorization': f'Bearer {secret_key}',
                    'Content-Type': 'application/json'
                },
                timeout=30.0  # Add timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] and data['data']['status'] == 'success':
                    # Verify amount if expected_amount is provided
                    if expected_amount is not None:
                        paid_amount = float(data['data']['amount']) / 100  # Convert from kobo/pesewas
                        if abs(paid_amount - expected_amount) > 0.01:  # Allow small difference due to floating point
                            return {
                                'success': False,
                                'message': f'Payment amount mismatch. Expected: {expected_amount}, Paid: {paid_amount}'
                            }
                    
                    print(f"Payment verified successfully for reference: {reference}")
                    return {
                        'success': True,
                        'data': {
                            **data['data'],
                            'email': data['data'].get('customer', {}).get('email'),
                            'reference': reference,
                            'amount': float(data['data']['amount']) / 100,
                            'currency': data['data']['currency'],
                            'payment_method': data['data'].get('channel', 'paystack')
                        }
                    }
            
            error_message = 'Payment verification failed'
            if response.status_code != 200:
                error_message = f'Paystack API error: {response.status_code}'
                print(f"Paystack API error response: {response.text}")
            
            return {
                'success': False,
                'message': error_message
            }
                
    except httpx.TimeoutException:
        print(f"Timeout verifying payment reference: {reference}")
        return {
            'success': False,
            'message': 'Payment verification timed out'
        }
    except Exception as e:
        print(f"Error verifying payment: {str(e)}")
        return {
            'success': False,
            'message': f'Error verifying payment: {str(e)}'
        } 