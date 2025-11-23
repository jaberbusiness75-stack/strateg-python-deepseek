class HybridConfluenceScalper:
    """الاستراتيجية الهجينة الرئيسية"""
    
    def __init__(self, live_trading=False):
        self.config = HybridConfig()
        self.analyzer = HybridAnalyzer(self.config)
        self.risk_manager = AdaptiveRiskManager(self.config)
        self.kill_zone_manager = KillZoneManager(self.config)
        self.live_trading = live_trading
        self.performance_tracker = PerformanceTracker()
    
    def run_hybrid_strategy(self):
        """تشغيل الاستراتيجية الهجينة"""
        print("Starting Hybrid Confluence Scalper Strategy...")
        
        while True:
            try:
                # تحديث ظروف السوق
                self._update_market_conditions()
                
                for pair in self.config.PAIRS:
                    if self._can_process_pair(pair):
                        self.process_hybrid_pair(pair)
                
                time.sleep(60)  # مراقبة مستمرة
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Strategy error: {e}")
                time.sleep(120)
    
    def process_hybrid_pair(self, pair):
        """معالجة زوج باستخدام المنهجية الهجينة"""
        # جمع البيانات متعددة الأطر
        market_data = self._gather_multi_timeframe_data(pair)
        
        # توليد الإشارة الهجينة
        signal = self.analyzer.generate_hybrid_signal(market_data)
        
        if signal:
            # التحقق من إدارة المخاطر
            can_trade, reason = self.risk_manager.can_trade(signal['quality'])
            
            if can_trade:
                self.execute_hybrid_trade(pair, signal)
            else:
                print(f"Trade rejected for {pair}: {reason}")
    
    def execute_hybrid_trade(self, pair, signal):
        """تنفيذ الصفقة الهجينة"""
        # حساب حجم المركز الديناميكي
        position_size = self.risk_manager.calculate_dynamic_position_size(
            signal['quality'], signal['entry_price'], signal['sl_price']
        )
        
        trade_execution = {
            'pair': pair,
            'direction': signal['direction'],
            'entry_price': signal['entry_price'],
            'sl_price': signal['sl_price'],
            'tp_price': signal['tp_price'],
            'position_size': position_size,
            'quality': signal['quality'],
            'score': signal['score'],
            'risk_multiplier': signal['risk_multiplier'],
            'details': signal['details'],
            'timestamp': datetime.now()
        }
        
        if self.live_trading:
            self._execute_live_trade(trade_execution)
        else:
            self._execute_simulated_trade(trade_execution)
        
        self.performance_tracker.record_trade(trade_execution)
        print(f"HYBRID TRADE EXECUTED: {trade_execution}")