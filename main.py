import time
import pandas as pd
from datetime import datetime
from hybrid_config import HybridConfig
from hybrid_analyzer import HybridAnalyzer
from adaptive_risk_manager import AdaptiveRiskManager
from kill_zone_manager import KillZoneManager
from data_aggregator import DataAggregator
from performance_tracker import PerformanceTracker
from execution_handler import ExecutionHandler

class HybridConfluenceScalper:
    """الاستراتيجية الهجينة الرئيسية المكتملة"""
    
    def __init__(self, live_trading=False, initial_capital=10000):
        self.config = HybridConfig()
        self.data_aggregator = DataAggregator(self.config)
        self.kill_zone_manager = KillZoneManager(self.config)
        self.analyzer = HybridAnalyzer(self.config)
        self.risk_manager = AdaptiveRiskManager(self.config, initial_capital)
        self.performance_tracker = PerformanceTracker()
        self.execution_handler = ExecutionHandler(live_trading)
        self.live_trading = live_trading
        
        print("🚀 Hybrid Confluence Scalper Initialized Successfully!")
        print(f"📊 Initial Capital: ${initial_capital:,.2f}")
        print(f"🎯 Trading Mode: {'LIVE' if live_trading else 'SIMULATION'}")
    
    def run_strategy(self):
        """تشغيل الاستراتيجية الهجينة بشكل مستمر"""
        print("\n" + "="*60)
        print("STARTING HYBRID CONFLUENCE SCALPER STRATEGY")
        print("="*60)
        
        iteration = 0
        while True:
            try:
                iteration += 1
                print(f"\n📈 Iteration {iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # تحديث ظروف السوق
                self._update_market_conditions()
                
                # معالجة كل زوج
                for pair in self.config.PAIRS:
                    self.process_hybrid_pair(pair)
                
                # مراقبة الصفقات النشطة
                completed_trades = self.execution_handler.monitor_trades()
                for trade in completed_trades:
                    self.performance_tracker.update_trade_result(
                        trade['order_id'], 
                        trade.get('exit_price', trade['executed_price']),
                        trade.get('exit_time', datetime.now())
                    )
                
                # عرض تقرير كل 10 iterations
                if iteration % 10 == 0:
                    print("\n" + "="*40)
                    print("PERFORMANCE UPDATE")
                    print("="*40)
                    print(self.performance_tracker.generate_report('ALL'))
                
                # انتظار للدورة التالية (1 دقيقة)
                time.sleep(60)
                
            except KeyboardInterrupt:
                print("\n🛑 Strategy stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                time.sleep(120)  # انتظار أطول في حالة الخطأ
    
    def _update_market_conditions(self):
        """تحديث ظروف السوق للجميع"""
        # الحصول على بيانات حديثة لأحد الأزواج لتقييم التقلبات
        sample_data = self.data_aggregator.get_multi_timeframe_data(self.config.PAIRS[0], '2d')
        if 'M15' in sample_data:
            self.risk_manager.update_market_conditions(sample_data['M15'])
    
    def _can_process_pair(self, pair):
        """التحقق من إمكانية معالجة الزوج"""
        # فحص Kill Zone والأخبار
        can_trade, reason = self.kill_zone_manager.can_trade(pair)
        if not can_trade:
            print(f"⏸️  Skipping {pair}: {reason}")
            return False
        
        # فحص حدود التداول اليومية
        can_trade_risk, risk_reason = self.risk_manager.can_trade('MEDIUM')  # استخدام MEDIUM كافتراضي
        if not can_trade_risk:
            print(f"⏸️  Risk limit for {pair}: {risk_reason}")
            return False
        
        return True
    
    def process_hybrid_pair(self, pair):
        """معالجة زوج باستخدام المنهجية الهجينة"""
        try:
            print(f"🔍 Analyzing {pair}...")
            
            # جمع البيانات متعددة الأطر
            market_data = self.data_aggregator.get_multi_timeframe_data(pair, '3d')
            
            if not market_data:
                print(f"❌ No data for {pair}")
                return
            
            # توليد الإشارة الهجينة
            signal = self.analyzer.generate_hybrid_signal(market_data)
            
            if signal:
                print(f"🎯 Signal generated for {pair}: {signal['direction']} (Score: {signal['score']}/10, Quality: {signal['quality']})")
                
                # حساب حجم المركز الديناميكي
                position_size = self.risk_manager.calculate_dynamic_position_size(
                    signal['quality'], signal['entry_price'], signal['sl_price']
                )
                
                signal['position_size'] = position_size
                signal['pair'] = pair
                
                # التحقق النهائي من إدارة المخاطر
                can_trade, reason = self.risk_manager.can_trade(signal['quality'])
                
                if can_trade:
                    self.execute_hybrid_trade(signal)
                else:
                    print(f"🚫 Trade rejected for {pair}: {reason}")
            else:
                print(f"➖ No valid signal for {pair}")
                
        except Exception as e:
            print(f"❌ Error processing {pair}: {e}")
    
    def execute_hybrid_trade(self, signal):
        """تنفيذ الصفقة الهجينة"""
        try:
            print(f"🚀 Executing {signal['direction']} trade for {signal['pair']}...")
            
            # تنفيذ الصفقة
            execution_result = self.execution_handler.execute_trade(signal, self.risk_manager.capital)
            
            if execution_result and execution_result['status'] == 'EXECUTED':
                # تسجيل الصفقة في tracker الأداء
                trade_id = self.performance_tracker.record_trade({
                    **signal,
                    'executed_price': execution_result['executed_price'],
                    'order_id': execution_result['order_id']
                })
                
                print(f"✅ Trade executed successfully!")
                print(f"   Pair: {signal['pair']}")
                print(f"   Direction: {signal['direction']}")
                print(f"   Entry: {execution_result['executed_price']:.5f}")
                print(f"   SL: {signal['sl_price']:.5f}")
                print(f"   TP: {signal['tp_price']:.5f}")
                print(f"   Size: {signal['position_size']}")
                print(f"   Quality: {signal['quality']}")
                print(f"   Score: {signal['score']}/10")
                
                # تحديث إدارة المخاطر
                self.risk_manager.daily_trades += 1
                
            else:
                print(f"❌ Trade execution failed")
                
        except Exception as e:
            print(f"❌ Error executing trade: {e}")
    
    def generate_final_report(self):
        """توليد تقرير نهائي مفصل"""
        print("\n" + "="*60)
        print("FINAL STRATEGY PERFORMANCE REPORT")
        print("="*60)
        
        report = self.performance_tracker.generate_report('ALL')
        print(report)
        
        # إحصائيات إضافية
        metrics = self.performance_tracker.calculate_performance_metrics('ALL')
        if metrics:
            print(f"\n📈 Additional Metrics:")
            print(f"   Best Quality: {max(metrics['quality_analysis'].items(), key=lambda x: x[1]['win_rate'])[0] if metrics['quality_analysis'] else 'N/A'}")
            print(f"   Avg Trade Duration: N/A")  # يمكن إضافته مع توقيت الخروج
            print(f"   Risk-Adjusted Return: {metrics['total_pnl'] / max(metrics['max_drawdown'], 1):.2f}")

if __name__ == "__main__":
    # Initialize strategy
    strategy = HybridConfluenceScalper(live_trading=False, initial_capital=10000)
    
    try:
        # Run strategy
        strategy.run_strategy()
    finally:
        # Generate final report
        strategy.generate_final_report()