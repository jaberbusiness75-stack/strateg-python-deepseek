from datetime import datetime, time
import requests

class KillZoneManager:
    def __init__(self, config):
        self.config = config
        self.news_cache = {}
        self.last_news_check = None
    
    def is_kill_zone(self):
        """فحص إذا كان الوقت ضمن Kill Zones"""
        current_hour = datetime.utcnow().hour
        current_minute = datetime.utcnow().minute
        current_time = current_hour + current_minute/60
        
        for start, end in self.config.KILL_ZONES:
            if start <= current_time <= end:
                return True
        return False
    
    def get_active_kill_zone(self):
        """الحصول على Kill Zone النشط"""
        current_hour = datetime.utcnow().hour
        current_minute = datetime.utcnow().minute
        current_time = current_hour + current_minute/60
        
        zones = {
            (7, 10): "London Open",
            (12, 16): "New York Open", 
            (10, 12): "London-NY Overlap"
        }
        
        for zone, name in zones.items():
            if zone[0] <= current_time <= zone[1]:
                return name
        return None
    
    def check_high_impact_news(self, currencies=['USD', 'EUR', 'GBP']):
        """فحص الأخبار عالية التأثير"""
        try:
            # استخدام التقنية السابقة مع تحسينات
            url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                events = response.json()
                current_time = datetime.utcnow()
                
                high_impact = []
                for event in events:
                    if event.get('impact') == 'High':
                        event_time = datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
                        time_diff = (event_time - current_time).total_seconds() / 3600
                        
                        # حدث خلال الساعتين القادمتين أو حدث قبل ساعة
                        if -1 <= time_diff <= 2:
                            if any(currency in event.get('title', '') for currency in currencies):
                                high_impact.append({
                                    'title': event.get('title', ''),
                                    'time': event_time,
                                    'currency': event.get('currency', '')
                                })
                
                return high_impact
                
        except Exception as e:
            print(f"Error checking news: {e}")
        
        return []
    
    def get_market_session(self):
        """تحديد جلسة السوق الحالية"""
        current_hour = datetime.utcnow().hour
        
        if 0 <= current_hour < 5:
            return "ASIA"
        elif 5 <= current_hour < 8:
            return "ASIA_EUROPE_OVERLAP"
        elif 8 <= current_hour < 12:
            return "LONDON"
        elif 12 <= current_hour < 16:
            return "LONDON_NY_OVERLAP"
        elif 16 <= current_hour < 21:
            return "NEW_YORK"
        else:
            return "LATE_NY"
    
    def can_trade(self, pair):
        """التحقق من إمكانية التداول للزوج"""
        # فحص Kill Zone
        if not self.is_kill_zone():
            return False, "Not in active Kill Zone"
        
        # فحص الأخبار
        base_currency = pair[:3]
        quote_currency = pair[3:]
        relevant_currencies = [base_currency, quote_currency]
        
        high_impact_news = self.check_high_impact_news(relevant_currencies)
        if high_impact_news:
            news_titles = [news['title'] for news in high_impact_news[:2]]
            return False, f"High impact news: {news_titles}"
        
        return True, "OK"