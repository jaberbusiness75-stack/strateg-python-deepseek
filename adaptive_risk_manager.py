class AdaptiveRiskManager:
    """مدير مخاطر تلقائي يتكيف مع ظروف السوق"""
    
    def __init__(self, config, initial_capital=10000):
        self.config = config
        self.capital = initial_capital
        self.daily_trades = 0
        self.market_volatility = 'NORMAL'
    
    def calculate_dynamic_position_size(self, signal_quality, entry_price, sl_price):
        """حجم مركز ديناميكي"""
        base_risk = self.config.BASE_RISK
        
        # تعديل المخاطرة بناء على جودة الإشارة
        quality_adjustment = {
            'HIGH': 1.5,
            'MEDIUM': 1.0,
            'LOW': 0.5
        }
        
        # تعديل بناء على تقلبات السوق
        volatility_adjustment = {
            'HIGH': 0.7,
            'NORMAL': 1.0,
            'LOW': 1.2
        }
        
        adjusted_risk = base_risk * quality_adjustment.get(signal_quality, 1.0)
        adjusted_risk *= volatility_adjustment.get(self.market_volatility, 1.0)
        
        risk_amount = self.capital * adjusted_risk
        pip_risk = abs(entry_price - sl_price) / 0.0001
        
        position_size = risk_amount / (pip_risk * 10)  # $10 per pip
        return round(max(0.01, position_size), 2)
    
    def update_market_conditions(self, recent_data):
        """تحديث ظروف السوق"""
        volatility = self._calculate_volatility(recent_data)
        
        if volatility > 0.008:  # 80 pips
            self.market_volatility = 'HIGH'
        elif volatility < 0.004:  # 40 pips
            self.market_volatility = 'LOW'
        else:
            self.market_volatility = 'NORMAL'
    
    def can_trade(self, signal_quality):
        """التحقق من إمكانية التداول"""
        if self.daily_trades >= self.config.MAX_DAILY_TRADES:
            return False, "Daily limit reached"
        
        if self.market_volatility == 'HIGH' and signal_quality == 'LOW':
            return False, "High volatility requires high quality signals"
        
        return True, "OK"