import uuid
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class OrderStatus:
    PENDING_SUBMIT = "PENDING_SUBMIT"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    UNKNOWN = "UNKNOWN"
    FAILED_TO_SUBMIT = "FAILED_TO_SUBMIT"

class OrderStateMachine:
    """
    The Master Execution Veto and Reconciliation Protocol.
    Prevents 'Zombie Orders' by generating a unique Client Order ID (clientOid)
    locally BEFORE the request ever leaves our servers. 
    
    If the API times out (HTTP 504), we query the exchange using OUR determinisitic ID,
    ensuring we never accidentally double-submit an order that was actually filled 
    during the timeout.
    """
    def __init__(self, exchange_adapter):
        """
        :param exchange_adapter: The CCXT Async instance (or similar REST adapter) with execution permissions.
        """
        self.exchange = exchange_adapter
        # Local state cache (In production, this is backed by PostgreSQL)
        self.active_orders: Dict[str, dict] = {}

    def generate_deterministic_id(self) -> str:
        """
        Generates a universally unique identifier (UUID v4) for the order.
        This is the bedrock of the State Machine.
        """
        return str(uuid.uuid4())

    async def submit_order(self, symbol: str, side: str, order_type: str, amount: float, price: float = None) -> dict:
        """
        The only mechanism authorized to place an order.
        Enforces the state transition from PENDING -> ACKNOWLEDGED.
        """
        # 1. State: PENDING_SUBMIT
        client_oid = self.generate_deterministic_id()
        
        order_record = {
            "client_oid": client_oid,
            "exchange_id": None, # Provided by the exchange, we do NOT rely on this
            "symbol": symbol,
            "side": side.upper(),
            "type": order_type.upper(),
            "amount": amount,
            "price": price,
            "status": OrderStatus.PENDING_SUBMIT,
            "created_at": datetime.utcnow()
        }
        
        # Save state to local memory (DB write should happen here in prod)
        self.active_orders[client_oid] = order_record
        logger.info(f"[{client_oid}] State: PENDING_SUBMIT. Attempting execution for {amount} {symbol}...")

        try:
            # Note: `create_order` in ccxt respects the `clientOrderId` param across major exchanges
            exchange_params = {'clientOrderId': client_oid}
            
            # The actual API network call
            exchange_response = await self.exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=amount,
                price=price,
                params=exchange_params
            )

            # 2. State: ACKNOWLEDGED (or FILLED if it was a market order)
            self.active_orders[client_oid]["exchange_id"] = exchange_response['id']
            self.active_orders[client_oid]["status"] = OrderStatus.ACKNOWLEDGED
            
            logger.info(f"[{client_oid}] State: ACKNOWLEDGED. Exchange accepted order.")
            return self.active_orders[client_oid]

        except Exception as e:
            error_message = str(e).lower()
            
            # 3. State: UNKNOWN (API Timeout, 502 Bad Gateway, 504 Gateway Timeout)
            # This is the most dangerous state. We DO NOT know if the order executed.
            if "timeout" in error_message or "gateway" in error_message:
                self.active_orders[client_oid]["status"] = OrderStatus.UNKNOWN
                logger.error(f"[{client_oid}] State: UNKNOWN. API Timeout. Commencing Reconciliation Protocol.")
                
                # Immediately fire off the reconciliation protocol
                await self.reconcile_unknown_order(client_oid, symbol)
                return self.active_orders[client_oid]
                
            else:
                # E.g., Insufficient funds, invalid symbol
                self.active_orders[client_oid]["status"] = OrderStatus.FAILED_TO_SUBMIT
                logger.error(f"[{client_oid}] State: FAILED_TO_SUBMIT. Exchange rejected. Reason: {str(e)}")
                return self.active_orders[client_oid]


    async def reconcile_unknown_order(self, client_oid: str, symbol: str):
        """
        Rescue protocol for UNKNOWN states.
        Queries the exchange continuously using our local `client_oid`.
        """
        logger.warning(f"Reconciling zombie order {client_oid}...")
        
        max_retries = 5
        base_delay = 1 # Exponential backoff
        
        for attempt in range(max_retries):
            try:
                # Fetch order by OUR ID, not the Exchange's ID
                # This guarantees we find the ghost order if it actually reached the matching engine
                status_response = await self.exchange.fetch_order(client_oid, symbol)
                
                # Rescue Successful!
                exchange_status = status_response['status'].upper()
                
                if exchange_status == 'CLOSED':
                    self.active_orders[client_oid]['status'] = OrderStatus.FILLED
                elif exchange_status == 'OPEN':
                    self.active_orders[client_oid]['status'] = OrderStatus.ACKNOWLEDGED
                elif exchange_status == 'CANCELED':
                    self.active_orders[client_oid]['status'] = OrderStatus.CANCELED
                    
                self.active_orders[client_oid]['exchange_id'] = status_response['id']
                
                logger.info(f"[{client_oid}] Reconciliation SUCCESS. True State: {self.active_orders[client_oid]['status']}")
                return

            except Exception as e:
                logger.error(f"Reconciliation attempt {attempt+1} failed: {str(e)}")
                
                import asyncio
                await asyncio.sleep(base_delay * (2 ** attempt))
                
        # If we max out retries, we assume the order never hit the matching engine,
        # but manual risk intervention is heavily recommended.
        logger.critical(f"[{client_oid}] RECONCILIATION FAILED. Order state remains permanently UNKNOWN. Engage manual Risk Veto.")
