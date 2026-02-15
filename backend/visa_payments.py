"""
Visa Developer API Integration for Agent Workflow Marketplace

APIs used:
1. CyberSource - Payment processing (buy tokens)
2. Visa Direct - Push payments to creators (payouts)
3. Visa Token Service - Secure card tokenization

Prize target: Visa — The Generative Edge: Future of Commerce
"""

import os
import json
import time
import hmac
import hashlib
import base64
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify

# Visa API Configuration
VISA_API_KEY = os.getenv("VISA_API_KEY")
VISA_USER_ID = os.getenv("VISA_USER_ID")
VISA_PASSWORD = os.getenv("VISA_PASSWORD")
VISA_SHARED_SECRET = os.getenv("VISA_SHARED_SECRET")
VISA_MERCHANT_ID = os.getenv("VISA_MERCHANT_ID")

# CyberSource Configuration
CYBERSOURCE_URL = os.getenv("CYBERSOURCE_URL", "https://apitest.cybersource.com")  # test environment
VISA_DIRECT_URL = os.getenv("VISA_DIRECT_URL", "https://sandbox.api.visa.com/visadirect")

visa_bp = Blueprint('visa_payments', __name__)


class VisaPaymentService:
    """
    Visa Developer API service for payment processing and payouts.
    """

    def __init__(self):
        self.api_key = VISA_API_KEY
        self.user_id = VISA_USER_ID
        self.password = VISA_PASSWORD
        self.shared_secret = VISA_SHARED_SECRET
        self.merchant_id = VISA_MERCHANT_ID

    # ============================================================================
    # CYBERSOURCE - Payment Processing (Buy Tokens)
    # ============================================================================

    def generate_cybersource_signature(self, payload: Dict) -> str:
        """
        Generate HMAC-SHA256 signature for CyberSource API request.
        Required for authentication.
        """
        # Create string to sign from payload
        signed_field_names = payload.get("signed_field_names", "").split(",")
        data_to_sign = []

        for field in signed_field_names:
            if field in payload:
                data_to_sign.append(f"{field}={payload[field]}")

        data_string = ",".join(data_to_sign)

        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            self.shared_secret.encode('utf-8'),
            data_string.encode('utf-8'),
            hashlib.sha256
        ).digest()

        return base64.b64encode(signature).decode('utf-8')

    def create_payment_session(
        self,
        user_id: str,
        token_package: str,
        amount_usd: float
    ) -> Dict[str, Any]:
        """
        Create a CyberSource payment session for token purchase.

        Args:
            user_id: User ID from your system
            token_package: Package type (starter, pro, enterprise)
            amount_usd: Amount in USD (e.g., 10.00)

        Returns:
            Dict with payment session details and form data
        """

        # Map token packages to token amounts
        token_amounts = {
            'starter': 1000,
            'pro': 5000,
            'enterprise': 15000,
        }

        tokens = token_amounts.get(token_package, 1000)

        # Generate unique transaction reference
        transaction_uuid = f"txn_{int(time.time())}_{user_id}"

        # Prepare CyberSource payment payload
        payload = {
            "access_key": self.api_key,
            "profile_id": self.merchant_id,
            "transaction_uuid": transaction_uuid,
            "transaction_type": "sale",
            "reference_number": transaction_uuid,
            "amount": f"{amount_usd:.2f}",
            "currency": "USD",
            "locale": "en-us",

            # Custom fields for your marketplace
            "merchant_defined_data1": user_id,
            "merchant_defined_data2": token_package,
            "merchant_defined_data3": str(tokens),

            # Payment details
            "payment_method": "card",
            "bill_to_forename": "Customer",
            "bill_to_surname": "Name",
            "bill_to_email": f"{user_id}@example.com",

            # Signature fields
            "signed_date_time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "signed_field_names": "access_key,profile_id,transaction_uuid,transaction_type,reference_number,amount,currency,locale,payment_method,signed_field_names,signed_date_time,merchant_defined_data1,merchant_defined_data2,merchant_defined_data3",
            "unsigned_field_names": "",

            # Return URLs
            "override_custom_receipt_page": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/payment/success",
            "override_custom_cancel_page": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/payment/cancel",
        }

        # Generate signature
        payload["signature"] = self.generate_cybersource_signature(payload)

        return {
            "success": True,
            "payment_url": f"{CYBERSOURCE_URL}/pay",
            "transaction_id": transaction_uuid,
            "form_data": payload,
            "tokens": tokens,
            "amount_usd": amount_usd,
        }

    def verify_payment_response(self, response_data: Dict) -> Dict[str, Any]:
        """
        Verify CyberSource payment response signature and extract details.
        Call this when user returns from CyberSource payment page.

        Args:
            response_data: POST data from CyberSource callback

        Returns:
            Dict with verification result and payment details
        """
        # Verify signature
        received_signature = response_data.get("signature")

        # Recreate signature from response data
        expected_signature = self.generate_cybersource_signature(response_data)

        if received_signature != expected_signature:
            return {
                "success": False,
                "error": "Invalid signature - possible tampering",
            }

        # Check payment decision
        decision = response_data.get("decision", "").upper()

        if decision == "ACCEPT":
            return {
                "success": True,
                "transaction_id": response_data.get("transaction_id"),
                "reference_number": response_data.get("reference_number"),
                "user_id": response_data.get("merchant_defined_data1"),
                "token_package": response_data.get("merchant_defined_data2"),
                "tokens": int(response_data.get("merchant_defined_data3", 0)),
                "amount": float(response_data.get("auth_amount", 0)),
                "message": "Payment successful",
            }
        elif decision == "DECLINE":
            return {
                "success": False,
                "error": "Payment declined",
                "reason": response_data.get("reason_code"),
            }
        else:
            return {
                "success": False,
                "error": "Payment under review",
                "decision": decision,
            }

    # ============================================================================
    # VISA DIRECT - Creator Payouts (Push to Card)
    # ============================================================================

    def generate_visa_direct_headers(self) -> Dict[str, str]:
        """Generate authentication headers for Visa Direct API."""
        # Basic Auth with user_id:password
        credentials = f"{self.user_id}:{self.password}"
        encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

        return {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": self.api_key,
        }

    def payout_to_creator(
        self,
        creator_id: str,
        card_number: str,
        amount_usd: float,
        workflow_id: str,
        description: str = "Workflow sale payout"
    ) -> Dict[str, Any]:
        """
        Send instant payout to workflow creator using Visa Direct.
        Push funds directly to their debit card.

        Args:
            creator_id: Creator's user ID
            card_number: Creator's Visa/debit card number (last 4 stored, full for payout)
            amount_usd: Amount to pay in USD
            workflow_id: Workflow that was purchased
            description: Transaction description

        Returns:
            Dict with payout status
        """

        # Generate unique identifiers
        system_trace = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
        transaction_id = f"payout_{int(time.time())}_{creator_id}"

        # Visa Direct Push Payment payload
        payload = {
            "systemsTraceAuditNumber": system_trace,
            "retrievalReferenceNumber": transaction_id[:12],
            "localTransactionDateTime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),

            # Amount
            "amount": f"{amount_usd:.2f}",
            "surcharge": "0.00",

            # Card details
            "cardAcceptor": {
                "name": "Agent Workflow Marketplace",
                "terminalId": "AWMKT001",
                "idCode": self.merchant_id,
                "address": {
                    "state": "CA",
                    "county": "San Mateo",
                    "country": "USA",
                    "zipCode": "94404",
                },
            },

            # Recipient card
            "recipientPrimaryAccountNumber": card_number,

            # Sender info
            "senderAccountNumber": self.merchant_id,
            "senderName": "Agent Marketplace",
            "senderAddress": "123 Market St, San Francisco, CA 94105",
            "senderCity": "San Francisco",
            "senderStateCode": "CA",
            "senderCountryCode": "USA",

            # Transaction purpose
            "transactionPurpose": "08",  # 08 = Payout/disbursement
            "businessApplicationId": "PP",  # Person-to-Person

            # Merchant metadata
            "merchantCategoryCode": "6012",  # Financial institutions
            "sourceOfFundsCode": "05",  # Credit/debit account

            # Custom data
            "merchantVerificationValue": creator_id,
            "transactionIdentifier": transaction_id,
        }

        # Make API request
        url = f"{VISA_DIRECT_URL}/fundstransfer/v1/pullfundstransactions"

        try:
            response = requests.post(
                url,
                headers=self.generate_visa_direct_headers(),
                json=payload,
                timeout=30
            )

            result = response.json()

            if response.status_code == 200:
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "status": result.get("actionCode"),
                    "approval_code": result.get("approvalCode"),
                    "amount": amount_usd,
                    "creator_id": creator_id,
                    "workflow_id": workflow_id,
                    "message": "Payout successful - funds pushed to card",
                    "response": result,
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Payout failed"),
                    "status_code": response.status_code,
                    "response": result,
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Payout request failed",
            }

    # ============================================================================
    # TOKEN CONVERSION HELPERS
    # ============================================================================

    def tokens_to_usd(self, tokens: int) -> float:
        """Convert tokens to USD. 100 tokens = $1.00"""
        return tokens / 100.0

    def usd_to_tokens(self, usd: float) -> int:
        """Convert USD to tokens. $1.00 = 100 tokens"""
        return int(usd * 100)


# ============================================================================
# FLASK ENDPOINTS
# ============================================================================

visa_service = VisaPaymentService()


@visa_bp.route('/api/visa/create-payment', methods=['POST'])
def create_visa_payment():
    """
    Create a Visa payment session for token purchase.

    Request:
    {
        "user_id": "user123",
        "token_package": "pro",  // starter, pro, enterprise
    }

    Response:
    {
        "payment_url": "https://...",
        "form_data": {...},
        "transaction_id": "txn_...",
        "tokens": 5000,
        "amount_usd": 45.00
    }
    """
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        token_package = data.get('token_package', 'starter')

        # Package pricing
        pricing = {
            'starter': 10.00,
            'pro': 45.00,
            'enterprise': 120.00,
        }

        amount_usd = pricing.get(token_package, 10.00)

        result = visa_service.create_payment_session(
            user_id=user_id,
            token_package=token_package,
            amount_usd=amount_usd
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@visa_bp.route('/api/visa/payment-callback', methods=['POST'])
def visa_payment_callback():
    """
    Handle CyberSource payment callback.
    Verify signature and credit tokens to user account.
    """
    try:
        # Get payment response data
        response_data = request.form.to_dict()

        # Verify payment
        verification = visa_service.verify_payment_response(response_data)

        if not verification['success']:
            return jsonify(verification), 400

        # Payment successful - credit tokens to user
        user_id = verification['user_id']
        tokens = verification['tokens']

        # Update user balance (integrate with commerce.py)
        from commerce import CommerceEngine
        commerce = CommerceEngine()
        deposit_result = commerce.deposit(user_id, tokens)

        # Log transaction
        print(f"✅ Visa payment successful: {user_id} received {tokens} tokens (${verification['amount']})")

        return jsonify({
            "success": True,
            "user_id": user_id,
            "tokens_credited": tokens,
            "new_balance": deposit_result['new_balance'],
            "transaction_id": verification['transaction_id'],
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@visa_bp.route('/api/visa/payout-creator', methods=['POST'])
def payout_creator():
    """
    Send instant payout to workflow creator via Visa Direct.

    Request:
    {
        "creator_id": "creator123",
        "card_number": "4111111111111111",  // Creator's Visa card
        "amount_tokens": 1700,  // 85% of 2000 token sale
        "workflow_id": "ohio_w2_itemized_2024"
    }

    Response:
    {
        "success": true,
        "transaction_id": "payout_...",
        "amount_usd": 17.00,
        "status": "approved"
    }
    """
    try:
        data = request.json
        creator_id = data.get('creator_id')
        card_number = data.get('card_number')
        amount_tokens = data.get('amount_tokens')
        workflow_id = data.get('workflow_id')

        if not all([creator_id, card_number, amount_tokens, workflow_id]):
            return jsonify({"error": "Missing required fields"}), 400

        # Convert tokens to USD
        amount_usd = visa_service.tokens_to_usd(amount_tokens)

        # Send payout via Visa Direct
        result = visa_service.payout_to_creator(
            creator_id=creator_id,
            card_number=card_number,
            amount_usd=amount_usd,
            workflow_id=workflow_id,
            description=f"Payout for workflow {workflow_id}"
        )

        if result['success']:
            print(f"💰 Visa Direct payout: ${amount_usd:.2f} to creator {creator_id}")

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@visa_bp.route('/api/visa/health', methods=['GET'])
def visa_health():
    """Check Visa API configuration."""
    return jsonify({
        "visa_configured": all([
            VISA_API_KEY,
            VISA_USER_ID,
            VISA_PASSWORD,
            VISA_SHARED_SECRET,
            VISA_MERCHANT_ID,
        ]),
        "cybersource_url": CYBERSOURCE_URL,
        "visa_direct_url": VISA_DIRECT_URL,
    })
