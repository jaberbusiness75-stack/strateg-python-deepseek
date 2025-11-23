class HybridConfig:
    """تهيئة الاستراتيجية الهجينة"""
    
    PAIRS = ['EURUSD', 'GBPUSD', 'USDJPY']
    
    # الأطر الزمنية الذكية
    TIMEFRAMES = {
        'H1': '1h',    # الاتجاه
        'M15': '15m',  # الزخم
        'M5': '5m',    # التحضير
        'M3': '3m',    # الدخول
        'M1': '1m'     # التأكيد
    }
    
    # Kill Zones موسعة
    KILL_ZONES = [
        (7, 10),    # لندن مفتوحة
        (12, 16),   # نيويورك مفتوحة
        (10, 12)    # التداخل
    ]
    
    # نظام النقاط المتعدد
    SCORING_SYSTEM = {
        'kill_zone': 2,
        'bias_alignment': 2,
        'liquidity_sweep': 2,
        'choch': 2,
        'volume_spike': 1,
        'rsi_confirmation': 1,
        'ema_alignment': 1,
        'dxy_confirmation': 1
    }
    
    MINIMUM_SCORE = 6
    MAX_DAILY_TRADES = 4
    BASE_RISK = 0.005  # 0.5%