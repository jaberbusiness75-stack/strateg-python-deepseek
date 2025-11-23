import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class PerformanceTracker:
    """تتبع وتحليل أداء التداول"""
    
    def __init__(self):
        self.trades = []
        self.daily_stats = {
            'date': None,
            'trades_count': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0,
            'max_drawdown': 0
        }
    
    def record_trade(self, trade_info):
        """تسجيل صفقة جديدة"""
        trade_record = {
            'id': len(self.trades) + 1,
            'pair': trade_info['pair'],
            'direction': trade_info['direction'],
            'entry_price': trade_info['entry_price'],
            'sl_price': trade_info['sl_price'],
            'tp_price': trade_info['tp_price'],
            'position_size': trade_info['position_size'],
            'quality': trade_info['quality'],
            'score': trade_info['score'],
            'timestamp': trade_info['timestamp'],
            'exit_price': None,
            'exit_time': None,
            'pnl': None,
            'pnl_pips': None,
            'result': None,  # WIN/LOSS
            'rr_ratio': None
        }
        self.trades.append(trade_record)
        return trade_record['id']
    
    def update_trade_result(self, trade_id, exit_price, exit_time):
        """تحديث نتيجة الصفقة"""
        for trade in self.trades:
            if trade['id'] == trade_id:
                trade['exit_price'] = exit_price
                trade['exit_time'] = exit_time
                
                # حساب P&L
                if trade['direction'] == 'LONG':
                    pnl_pips = (exit_price - trade['entry_price']) / 0.0001
                else:
                    pnl_pips = (trade['entry_price'] - exit_price) / 0.0001
                
                trade['pnl_pips'] = pnl_pips
                trade['pnl'] = pnl_pips * trade['position_size'] * 10  # $10 per pip
                
                # تحديد النتيجة
                trade['result'] = 'WIN' if trade['pnl'] > 0 else 'LOSS'
                
                # حساب نسبة R:R
                risk_pips = abs(trade['entry_price'] - trade['sl_price']) / 0.0001
                reward_pips = abs(trade['entry_price'] - trade['tp_price']) / 0.0001
                trade['rr_ratio'] = reward_pips / risk_pips if risk_pips > 0 else 0
                break
    
    def calculate_performance_metrics(self, period='ALL'):
        """حساب مقاييس الأداء"""
        if not self.trades:
            return {}
        
        df_trades = pd.DataFrame(self.trades)
        df_trades = df_trades[df_trades['result'].notna()]
        
        if df_trades.empty:
            return {}
        
        # الفلترة حسب الفترة
        if period != 'ALL':
            if period == 'WEEK':
                cutoff_date = datetime.now() - timedelta(days=7)
            elif period == 'MONTH':
                cutoff_date = datetime.now() - timedelta(days=30)
            df_trades = df_trades[df_trades['timestamp'] >= cutoff_date]
        
        winning_trades = df_trades[df_trades['result'] == 'WIN']
        losing_trades = df_trades[df_trades['result'] == 'LOSS']
        
        total_trades = len(df_trades)
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        
        total_pnl = df_trades['pnl'].sum()
        avg_win = winning_trades['pnl'].mean() if not winning_trades.empty else 0
        avg_loss = losing_trades['pnl'].mean() if not losing_trades.empty else 0
        
        # نسبة البروفيت فاكتور
        gross_profit = winning_trades['pnl'].sum()
        gross_loss = abs(losing_trades['pnl'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # أقصى انخفاض
        cumulative_pnl = df_trades['pnl'].cumsum()
        running_max = cumulative_pnl.expanding().max()
        drawdown = running_max - cumulative_pnl
        max_drawdown = drawdown.max()
        
        # تحليل حسب جودة الإشارة
        quality_analysis = {}
        for quality in ['HIGH', 'MEDIUM', 'LOW']:
            quality_trades = df_trades[df_trades['quality'] == quality]
            if not quality_trades.empty:
                quality_win_rate = (quality_trades['result'] == 'WIN').mean()
                quality_analysis[quality] = {
                    'win_rate': quality_win_rate,
                    'count': len(quality_trades),
                    'avg_pnl': quality_trades['pnl'].mean()
                }
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'avg_rr_ratio': df_trades['rr_ratio'].mean(),
            'quality_analysis': quality_analysis,
            'best_pair': df_trades.groupby('pair')['pnl'].sum().idxmax() if len(df_trades['pair'].unique()) > 0 else 'N/A'
        }
    
    def generate_report(self, period='ALL'):
        """توليد تقرير أداء"""
        metrics = self.calculate_performance_metrics(period)
        
        if not metrics:
            return "No trades to analyze"
        
        report = [
            "=" * 60,
            "HYBRID CONFLUENCE SCALPER - PERFORMANCE REPORT",
            "=" * 60,
            f"Period: {period}",
            f"Total Trades: {metrics['total_trades']}",
            f"Win Rate: {metrics['win_rate']:.2%}",
            f"Total P&L: ${metrics['total_pnl']:.2f}",
            f"Profit Factor: {metrics['profit_factor']:.2f}",
            f"Max Drawdown: ${metrics['max_drawdown']:.2f}",
            f"Average R:R: {metrics['avg_rr_ratio']:.2f}",
            "",
            "QUALITY ANALYSIS:"
        ]
        
        for quality, stats in metrics['quality_analysis'].items():
            report.append(f"  {quality}: {stats['count']} trades, {stats['win_rate']:.2%} win rate, Avg P&L: ${stats['avg_pnl']:.2f}")
        
        report.extend([
            "",
            f"Best Performing Pair: {metrics['best_pair']}",
            "=" * 60
        ])
        
        return "\n".join(report)