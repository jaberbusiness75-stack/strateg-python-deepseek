import yfinance as yf
import pandas as pd
import numpy as np
from talib import EMA, RSI, ATR
import time

class DataAggregator:
    """مجمع البيانات متعددة الأطر الزمنية"""
    
    def __init__(self, config):
        self.config = config
        self.data_cache = {}
    
    def get_multi_timeframe_data(self, pair, period='5d'):
        """جمع بيانات متعددة الأطر الزمنية"""
        yf_symbol = f"{pair[:3]}=X"
        multi_tf_data = {}
        
        for tf_name, tf_interval in self.config.TIMEFRAMES.items():
            try:
                # استخدام cache لتجنب الطلبات المتكررة
                cache_key = f"{pair}_{tf_name}"
                if cache_key in self.data_cache:
                    data = self.data_cache[cache_key]
                else:
                    data = yf.download(yf_symbol, period=period, interval=tf_interval)
                    self.data_cache[cache_key] = data
                
                if not data.empty:
                    # إضافة المؤشرات التقنية
                    data = self._add_technical_indicators(data, tf_name)
                    multi_tf_data[tf_name] = data
                    
            except Exception as e:
                print(f"Error fetching {tf_name} data for {pair}: {e}")
                continue
        
        return multi_tf_data
    
    def _add_technical_indicators(self, df, timeframe):
        """إضافة المؤشرات التقنية للبيانات"""
        # المتوسطات المتحركة
        for period in [20, 50, 200]:
            df[f'EMA_{period}'] = EMA(df['Close'], timeperiod=period)
        
        # RSI
        df['RSI'] = RSI(df['Close'], timeperiod=14)
        
        # ATR للتقلبات
        df['ATR'] = ATR(df['High'], df['Low'], df['Close'], timeperiod=14)
        
        # حساب الزخم
        df['Momentum_5'] = df['Close'] / df['Close'].shift(5) - 1
        
        # تحديد القمم والقيعان
        df = self._find_swing_points(df)
        
        return df
    
    def _find_swing_points(self, df, window=3):
        """تحديد نقاط التقلب (Swing Points)"""
        # قمم
        df['is_swing_high'] = (df['High'] == df['High'].rolling(window=window*2+1, center=True).max())
        df['is_swing_low'] = (df['Low'] == df['Low'].rolling(window=window*2+1, center=True).min())
        
        # تصفية القمم والقيعان المهمة فقط
        swing_highs = df[df['is_swing_high']]['High']
        swing_lows = df[df['is_swing_low']]['Low']
        
        df['recent_swing_high'] = swing_highs.rolling(window=5).max()
        df['recent_swing_low'] = swing_lows.rolling(window=5).min()
        
        return df
    
    def calculate_market_volatility(self, df):
        """حساب تقلبات السوق"""
        if 'ATR' in df.columns:
            current_atr = df['ATR'].iloc[-1]
            avg_atr = df['ATR'].tail(20).mean()
            
            volatility_ratio = current_atr / avg_atr if avg_atr > 0 else 1
            
            if volatility_ratio > 1.3:
                return 'HIGH'
            elif volatility_ratio < 0.7:
                return 'LOW'
            else:
                return 'NORMAL'
        return 'NORMAL'
    
    def detect_trend_strength(self, df):
        """كشف قوة الاتجاه"""
        if 'EMA_50' not in df.columns or 'EMA_200' not in df.columns:
            return 'NEUTRAL'
        
        current_price = df['Close'].iloc[-1]
        ema_20 = df['EMA_20'].iloc[-1]
        ema_50 = df['EMA_50'].iloc[-1]
        ema_200 = df['EMA_200'].iloc[-1]
        
        # ترتيب المتوسطات المتحركة
        if current_price > ema_20 > ema_50 > ema_200:
            return 'STRONG_BULLISH'
        elif current_price < ema_20 < ema_50 < ema_200:
            return 'STRONG_BEARISH'
        elif current_price > ema_50 > ema_200:
            return 'BULLISH'
        elif current_price < ema_50 < ema_200:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    def clear_cache(self):
        """مسح الذاكرة المؤقتة"""
        self.data_cache.clear()