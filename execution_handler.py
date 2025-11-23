import time
from datetime import datetime

class ExecutionHandler:
    """معالج تنفيذ الصفقات"""
    
    def __init__(self, live_trading=False, broker_api=None):
        self.live_trading = live_trading
        self.broker_api = broker_api
        self.pending_orders = []
        self.active_trades = []
    
    def execute_trade(self, trade_signal, capital=10000):
        """تنفيذ صفقة بناء على الإشارة"""
        try:
            # حساب حجم المركز النهائي
            position_size = trade_signal['position_size']
            
            # إعداد تفاصيل التنفيذ
            execution_details = {
                'pair': trade_signal['pair'],
                'direction': trade_signal['direction'],
                'entry_price': trade_signal['entry_price'],
                'sl_price': trade_signal['sl_price'],
                'tp_price': trade_signal['tp_price'],
                'position_size': position_size,
                'quality': trade_signal['quality'],
                'score': trade_signal['score'],
                'timestamp': datetime.now(),
                'status': 'PENDING'
            }
            
            if self.live_trading:
                result = self._execute_live(execution_details)
            else:
                result = self._execute_simulated(execution_details)
            
            execution_details.update(result)
            self.pending_orders.append(execution_details)
            
            return execution_details
            
        except Exception as e:
            print(f"Execution error: {e}")
            return None
    
    def _execute_live(self, execution_details):
        """تنفيذ حي مع وسيط"""
        if not self.broker_api:
            return {'status': 'ERROR', 'error': 'No broker API configured'}
        
        try:
            # هنا يتم دمج API الوسيط الحقيقي
            # هذا مثال افتراضي
            order_result = {
                'order_id': f"ORD_{int(time.time())}",
                'status': 'EXECUTED',
                'executed_price': execution_details['entry_price'],
                'execution_time': datetime.now()
            }
            
            # إضافة الصفقة للقائمة النشطة
            self.active_trades.append({
                **execution_details,
                **order_result
            })
            
            return order_result
            
        except Exception as e:
            return {'status': 'ERROR', 'error': str(e)}
    
    def _execute_simulated(self, execution_details):
        """تنفيذ محاكاة"""
        # محاكاة التنفيذ بسعر السوق الحالي
        simulated_result = {
            'order_id': f"SIM_{int(time.time())}",
            'status': 'EXECUTED',
            'executed_price': execution_details['entry_price'],
            'execution_time': datetime.now(),
            'commission': 0.0002,  # عمولة افتراضية
            'slippage': 0.0001    # انزلاق افتراضي
        }
        
        # تطبيق الانزلاق على سعر التنفيذ
        if execution_details['direction'] == 'BUY':
            simulated_result['executed_price'] += simulated_result['slippage']
        else:
            simulated_result['executed_price'] -= simulated_result['slippage']
        
        self.active_trades.append({
            **execution_details,
            **simulated_result
        })
        
        return simulated_result
    
    def monitor_trades(self):
        """مراقبة الصفقات النشطة"""
        completed_trades = []
        
        for trade in self.active_trades[:]:
            current_status = self._check_trade_status(trade)
            
            if current_status['status'] in ['CLOSED', 'STOPPED', 'TAKEN']:
                completed_trades.append({**trade, **current_status})
                self.active_trades.remove(trade)
        
        return completed_trades
    
    def _check_trade_status(self, trade):
        """فحص حالة الصفقة"""
        # في التنفيذ الحقيقي، يتم الاتصال بالوسيط
        # هنا محاكاة للوصول لأهداف الربح أو الخسارة
        
        # هذا قسم يحتاج لبيانات السوق الحالية من الوسيط
        # للتبسيط، نعود بحالة مستمرة
        return {
            'status': 'OPEN',
            'current_pnl': 0,
            'current_pnl_pips': 0
        }
    
    def close_trade(self, order_id, reason='MANUAL'):
        """إغلاق صفقة يدوياً"""
        for trade in self.active_trades:
            if trade['order_id'] == order_id:
                # تنفيذ إغلاق مع الوسيط
                if self.live_trading:
                    # تنفيذ حقيقي
                    pass
                else:
                    # تنفيذ محاكاة
                    trade['exit_reason'] = reason
                    trade['status'] = 'CLOSED'
                    trade['exit_time'] = datetime.now()
                
                return True
        return False