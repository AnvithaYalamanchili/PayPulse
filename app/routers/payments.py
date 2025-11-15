import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .subscriptions import get_current_user
import stripe
from datetime import datetime, timedelta
from .. import models

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY") 

print("Hello")
print("API_KEY:",stripe.api_key)
print(STRIPE_PUBLISHABLE_KEY)
router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/create-payment-intent")
def create_payment(plan_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    plan=db.query(models.Plan).filter(models.Plan.id==plan_id).first()
    if not plan:
        raise HTTPException(status_code=404,detail="Plan not found")
    existing_subscription=db.query(models.Subscription).filter(
        models.Subscription.user_id==current_user.id,
        models.Subscription.plan_id==plan.id,
        models.Subscription.status=="active",
        models.Subscription.end_date>=datetime.utcnow()
    ).first()

    if existing_subscription:
        raise HTTPException(status_code=400,detail="You already have an active subscription to this plan.")

    if plan.price==0:
        subscription=models.Subscription(
            user_id=current_user.id,
            plan_id=plan.id,
            status="active",
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow()+timedelta(days=30)
        )
        db.add(subscription),
        db.commit(),
        db.refresh(subscription)
        return {"message":"Subscription added for free plan","subscription_id":subscription.id}
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(plan.price*100), 
            currency="usd",
            metadata={"user_id": current_user.id,"plan_id":plan.id},
            automatic_payment_methods={
                "enabled": True,
                "allow_redirects": "never"  
            }
        )
        return {"client_secret": intent.client_secret}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/confirm-payment/{payment_intent_id}")
def confirm_payment(payment_intent_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        payment_intent = stripe.PaymentIntent.confirm(
            payment_intent_id,
            payment_method="pm_card_visa" 
        )

        if payment_intent.status != "succeeded":
            raise HTTPException(status_code=400, detail="Payment not successful")

        plan_id=int(payment_intent.metadata.get("plan_id"))
        if not plan_id:
            raise HTTPException(status_code=400, detail="Plan ID not found in payment metadata" )

        subscription=models.Subscription(
            user_id=current_user.id,
            plan_id=plan_id,
            status="active",
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow()+timedelta(days=30)
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)

        db_payment = models.Payment(
            user_id=current_user.id,
            subscription_id=subscription.id,
            amount=payment_intent.amount / 100,  
            currency=payment_intent.currency,
            status=payment_intent.status,
            payment_gateway_id=payment_intent.id,
        )

        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)

        return {"message": "Payment successful and subscription activated", "payment_id": db_payment.id,"subscription_id":subscription.id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
