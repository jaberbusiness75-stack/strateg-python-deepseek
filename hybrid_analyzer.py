class HybridAnalyzer:
    """محلل هجين يجمع بين مميزات الاستراتيجيتين"""
    
    def __init__(self, config):
        self.config = config
        self.confluence_score = 0
        self.signal_quality = 'LOW'
    
    def calculate_hybrid_score(self, market_data):
        """حساب النقاط الهجين"""
        score = 0
        score_details = []
        
        # 1. التوقيت والاتجاه (من Smart Scalp Pro)
        if self._is_kill_zone():
            score += self.config.SCORING_SYSTEM['kill_zone']
            score_details.append("Kill Zone Active")
        
        if self._check_bias_alignment(market_data):
            score += self.config.SCORING_SYSTEM['bias_alignment']
            score_details.append("Bias Alignment")
        
        # 2. التناغم التقني (من M5 Confluence)
        if self._detect_liquidity_sweep(market_data['M5']):
            score += self.config.SCORING_SYSTEM['liquidity_sweep']
            score_details.append("Liquidity Sweep")
        
        if self._detect_choch(market_data['M5']):
            score += self.config.SCORING_SYSTEM['choch']
            score_details.append("CHoCH Detected")
        
        # 3. التأكيدات الإضافية
        if self._check_volume_spike(market_data['M3']):
            score += self.config.SCORING_SYSTEM['volume_spike']
            score_details.append("Volume Spike")
        
        if self._check_rsi_confirmation(market_data['M5']):
            score += self.config.SCORING_SYSTEM['rsi_confirmation']
            score_details.append("RSI Confirmation")
        
        # تحديد جودة الإشارة
        if score >= 8:
            self.signal_quality = 'HIGH'
        elif score >= 6:
            self.signal_quality = 'MEDIUM'
        else:
            self.signal_quality = 'LOW'
        
        return score, score_details
    
    def generate_hybrid_signal(self, market_data):
        """توليد إشارة هجينة"""
        score, details = self.calculate_hybrid_score(market_data)
        
        if score < self.config.MINIMUM_SCORE:
            return None
        
        # تحديد اتجاه الصفقة
        direction = self._determine_direction(market_data)
        
        # حساب مستويات الدخول والخروج
        entry_levels = self._calculate_entry_levels(market_data, direction)
        risk_levels = self._calculate_risk_levels(entry_levels, direction)
        
        return {
            'direction': direction,
            'score': score,
            'quality': self.signal_quality,
            'details': details,
            'entry_price': entry_levels['optimal_entry'],
            'sl_price': risk_levels['stop_loss'],
            'tp_price': risk_levels['take_profit'],
            'risk_multiplier': self._get_risk_multiplier(),
            'timestamp': datetime.now()
        }
    
    def _get_risk_multiplier(self):
        """مضاعف المخاطرة بناء على جودة الإشارة"""
        multipliers = {
            'HIGH': 1.5,    # 0.75% risk
            'MEDIUM': 1.0,  # 0.5% risk
            'LOW': 0.5      # 0.25% risk
        }
        return multipliers.get(self.signal_quality, 1.0)