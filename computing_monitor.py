#!/usr/bin/env python3
"""
Computing Power Monitor and Credit System
Tracks CPU/GPU usage, processing time, and calculates credits
"""

import psutil
import time
import threading
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

try:
    import nvidia_ml_py3 as nvml
    NVIDIA_ML_AVAILABLE = True
    nvml.nvmlInit()
except ImportError:
    NVIDIA_ML_AVAILABLE = False

class ComputingMonitor:
    """Monitor computing resources and calculate credits"""
    
    def __init__(self):
        self.monitoring = False
        self.start_time = None
        self.end_time = None
        self.cpu_readings = []
        self.gpu_readings = []
        self.memory_readings = []
        self.gpu_memory_readings = []
        self.monitor_thread = None
        
        # Credit calculation settings
        self.credit_rates = {
            'cpu_per_minute': 1.0,      # Base credits per minute of CPU usage
            'gpu_per_minute': 3.0,      # Credits per minute of GPU usage (higher cost)
            'memory_gb_minute': 0.5,    # Credits per GB-minute of RAM usage
            'gpu_memory_gb_minute': 2.0, # Credits per GB-minute of GPU memory
            'time_multiplier': 1.2,     # Multiplier for longer processing times
            'video_type_multipliers': {
                'reel': 1.0,
                'avatar': 1.5,          # Avatar generation is more intensive
                'musical': 1.3          # Musical generation is moderately intensive
            }
        }
        
        # Performance tiers
        self.performance_tiers = {
            'basic': {'cpu_threshold': 50, 'multiplier': 1.0},
            'standard': {'cpu_threshold': 75, 'multiplier': 1.2},
            'high': {'cpu_threshold': 90, 'multiplier': 1.5},
            'extreme': {'cpu_threshold': 95, 'multiplier': 2.0}
        }
        
    def start_monitoring(self, video_type: str = 'reel'):
        """Start monitoring computing resources"""
        if self.monitoring:
            return False
        
        self.monitoring = True
        self.start_time = datetime.now()
        self.video_type = video_type
        self.cpu_readings = []
        self.gpu_readings = []
        self.memory_readings = []
        self.gpu_memory_readings = []
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print(f"🔧 Started computing monitor for {video_type} generation")
        return True
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return usage report"""
        if not self.monitoring:
            return {}
        
        self.monitoring = False
        self.end_time = datetime.now()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        
        report = self._generate_report()
        print(f"⏹️ Stopped computing monitor")
        
        return report
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Get CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.cpu_readings.append(cpu_percent)
                
                # Get memory usage
                memory = psutil.virtual_memory()
                memory_gb = memory.used / (1024**3)
                self.memory_readings.append(memory_gb)
                
                # Get GPU usage if available
                if GPU_AVAILABLE:
                    try:
                        gpus = GPUtil.getGPUs()
                        if gpus:
                            gpu = gpus[0]  # Use first GPU
                            self.gpu_readings.append(gpu.load * 100)
                            self.gpu_memory_readings.append(gpu.memoryUsed / 1024)  # Convert to GB
                        else:
                            self.gpu_readings.append(0)
                            self.gpu_memory_readings.append(0)
                    except:
                        self.gpu_readings.append(0)
                        self.gpu_memory_readings.append(0)
                else:
                    self.gpu_readings.append(0)
                    self.gpu_memory_readings.append(0)
                
                time.sleep(2)  # Monitor every 2 seconds
                
            except Exception as e:
                print(f"⚠️ Monitoring error: {e}")
                break
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate detailed usage report with credits"""
        if not self.start_time or not self.end_time:
            return {}
        
        duration = (self.end_time - self.start_time).total_seconds()
        duration_minutes = duration / 60
        
        # Calculate averages
        avg_cpu = sum(self.cpu_readings) / len(self.cpu_readings) if self.cpu_readings else 0
        avg_gpu = sum(self.gpu_readings) / len(self.gpu_readings) if self.gpu_readings else 0
        avg_memory = sum(self.memory_readings) / len(self.memory_readings) if self.memory_readings else 0
        avg_gpu_memory = sum(self.gpu_memory_readings) / len(self.gpu_memory_readings) if self.gpu_memory_readings else 0
        
        # Determine performance tier
        performance_tier = self._get_performance_tier(avg_cpu)
        
        # Calculate credits
        credits = self._calculate_credits(
            duration_minutes, avg_cpu, avg_gpu, avg_memory, avg_gpu_memory, performance_tier
        )
        
        report = {
            'duration': {
                'seconds': duration,
                'minutes': duration_minutes,
                'formatted': self._format_duration(duration)
            },
            'cpu': {
                'average_percent': round(avg_cpu, 1),
                'max_percent': max(self.cpu_readings) if self.cpu_readings else 0,
                'min_percent': min(self.cpu_readings) if self.cpu_readings else 0,
                'readings_count': len(self.cpu_readings)
            },
            'gpu': {
                'available': GPU_AVAILABLE and avg_gpu > 0,
                'average_percent': round(avg_gpu, 1),
                'max_percent': max(self.gpu_readings) if self.gpu_readings else 0,
                'memory_gb': round(avg_gpu_memory, 2)
            },
            'memory': {
                'average_gb': round(avg_memory, 2),
                'max_gb': round(max(self.memory_readings), 2) if self.memory_readings else 0
            },
            'performance': {
                'tier': performance_tier,
                'processing_type': 'GPU-Accelerated' if avg_gpu > 10 else 'CPU-Based'
            },
            'credits': credits,
            'video_type': getattr(self, 'video_type', 'unknown'),
            'timestamp': self.start_time.isoformat(),
            'system_info': self._get_system_info()
        }
        
        return report
    
    def _calculate_credits(self, duration_minutes: float, avg_cpu: float, avg_gpu: float, 
                          avg_memory: float, avg_gpu_memory: float, performance_tier: str) -> Dict[str, Any]:
        """Calculate credits based on resource usage"""
        
        # Base credits
        cpu_credits = (avg_cpu / 100) * duration_minutes * self.credit_rates['cpu_per_minute']
        gpu_credits = (avg_gpu / 100) * duration_minutes * self.credit_rates['gpu_per_minute']
        memory_credits = avg_memory * duration_minutes * self.credit_rates['memory_gb_minute']
        gpu_memory_credits = avg_gpu_memory * duration_minutes * self.credit_rates['gpu_memory_gb_minute']
        
        # Base total
        base_credits = cpu_credits + gpu_credits + memory_credits + gpu_memory_credits
        
        # Apply video type multiplier
        video_type = getattr(self, 'video_type', 'reel')
        type_multiplier = self.credit_rates['video_type_multipliers'].get(video_type, 1.0)
        
        # Apply performance tier multiplier
        tier_multiplier = self.performance_tiers[performance_tier]['multiplier']
        
        # Apply time multiplier for longer processes
        time_multiplier = 1.0 + (duration_minutes / 10) * 0.1  # +10% per 10 minutes
        time_multiplier = min(time_multiplier, 2.0)  # Cap at 200%
        
        # Final credits calculation
        final_credits = base_credits * type_multiplier * tier_multiplier * time_multiplier
        
        return {
            'breakdown': {
                'cpu_credits': round(cpu_credits, 2),
                'gpu_credits': round(gpu_credits, 2),
                'memory_credits': round(memory_credits, 2),
                'gpu_memory_credits': round(gpu_memory_credits, 2),
                'base_total': round(base_credits, 2)
            },
            'multipliers': {
                'video_type': type_multiplier,
                'performance_tier': tier_multiplier,
                'time_bonus': round(time_multiplier, 2)
            },
            'final_credits': round(final_credits, 2),
            'cost_per_minute': round(final_credits / duration_minutes, 2) if duration_minutes > 0 else 0
        }
    
    def _get_performance_tier(self, avg_cpu: float) -> str:
        """Determine performance tier based on CPU usage"""
        for tier, config in reversed(self.performance_tiers.items()):
            if avg_cpu >= config['cpu_threshold']:
                return tier
        return 'basic'
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            memory = psutil.virtual_memory()
            
            system_info = {
                'cpu_cores': cpu_count,
                'cpu_frequency_mhz': round(cpu_freq.current) if cpu_freq else 'Unknown',
                'total_memory_gb': round(memory.total / (1024**3), 1),
                'gpu_info': self._get_gpu_info()
            }
            
            return system_info
        except:
            return {'error': 'Could not retrieve system info'}
    
    def _get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU information"""
        if not GPU_AVAILABLE:
            return {'available': False, 'reason': 'GPUtil not installed'}
        
        try:
            gpus = GPUtil.getGPUs()
            if not gpus:
                return {'available': False, 'reason': 'No GPUs detected'}
            
            gpu = gpus[0]
            return {
                'available': True,
                'name': gpu.name,
                'memory_total_gb': round(gpu.memoryTotal / 1024, 1),
                'driver_version': gpu.driver if hasattr(gpu, 'driver') else 'Unknown'
            }
        except Exception as e:
            return {'available': False, 'error': str(e)}


class CreditManager:
    """Manage user credits and usage history"""
    
    def __init__(self, data_file: str = 'user_credits.json'):
        self.data_file = Path(data_file)
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load credit data from file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'balance': 100.0,  # Starting credits
            'total_used': 0.0,
            'total_earned': 100.0,
            'usage_history': [],
            'created': datetime.now().isoformat()
        }
    
    def _save_data(self):
        """Save credit data to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save credit data: {e}")
    
    def get_balance(self) -> float:
        """Get current credit balance"""
        return self.data.get('balance', 0.0)
    
    def add_credits(self, amount: float, reason: str = 'Manual addition'):
        """Add credits to user account"""
        self.data['balance'] += amount
        self.data['total_earned'] += amount
        
        self.data['usage_history'].append({
            'type': 'credit',
            'amount': amount,
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'balance_after': self.data['balance']
        })
        
        self._save_data()
        print(f"💰 Added {amount} credits. New balance: {self.data['balance']}")
    
    def deduct_credits(self, report: Dict[str, Any]) -> bool:
        """Deduct credits based on computing report"""
        credits_needed = report.get('credits', {}).get('final_credits', 0)
        
        if self.data['balance'] < credits_needed:
            print(f"❌ Insufficient credits! Need: {credits_needed}, Have: {self.data['balance']}")
            return False
        
        self.data['balance'] -= credits_needed
        self.data['total_used'] += credits_needed
        
        # Record usage
        self.data['usage_history'].append({
            'type': 'usage',
            'amount': -credits_needed,
            'video_type': report.get('video_type'),
            'duration': report.get('duration', {}).get('formatted'),
            'performance_tier': report.get('performance', {}).get('tier'),
            'processing_type': report.get('performance', {}).get('processing_type'),
            'timestamp': datetime.now().isoformat(),
            'balance_after': self.data['balance'],
            'detailed_report': report
        })
        
        self._save_data()
        print(f"💳 Deducted {credits_needed} credits. Remaining balance: {self.data['balance']}")
        return True
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        history = self.data.get('usage_history', [])
        
        # Filter recent usage (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_usage = [
            h for h in history 
            if h.get('type') == 'usage' and 
            datetime.fromisoformat(h['timestamp']) > thirty_days_ago
        ]
        
        stats = {
            'current_balance': self.data['balance'],
            'total_earned': self.data['total_earned'],
            'total_used': self.data['total_used'],
            'recent_usage_30_days': len(recent_usage),
            'average_credits_per_video': 0,
            'most_expensive_video_type': 'unknown',
            'total_videos_generated': len([h for h in history if h.get('type') == 'usage'])
        }
        
        if recent_usage:
            total_recent_credits = sum(abs(h['amount']) for h in recent_usage)
            stats['average_credits_per_video'] = round(total_recent_credits / len(recent_usage), 2)
            
            # Find most expensive video type
            video_types = {}
            for usage in recent_usage:
                vtype = usage.get('video_type', 'unknown')
                if vtype not in video_types:
                    video_types[vtype] = []
                video_types[vtype].append(abs(usage['amount']))
            
            if video_types:
                avg_by_type = {vtype: sum(costs)/len(costs) for vtype, costs in video_types.items()}
                stats['most_expensive_video_type'] = max(avg_by_type, key=avg_by_type.get)
        
        return stats


# Global instances
computing_monitor = ComputingMonitor()
credit_manager = CreditManager()

def start_monitoring(video_type: str = 'reel') -> bool:
    """Start monitoring computing resources"""
    return computing_monitor.start_monitoring(video_type)

def stop_monitoring_and_deduct_credits() -> Dict[str, Any]:
    """Stop monitoring and handle credit deduction"""
    report = computing_monitor.stop_monitoring()
    
    if report:
        # Check if user has enough credits
        credits_needed = report.get('credits', {}).get('final_credits', 0)
        current_balance = credit_manager.get_balance()
        
        if current_balance >= credits_needed:
            credit_manager.deduct_credits(report)
            report['credit_transaction'] = 'success'
        else:
            report['credit_transaction'] = 'insufficient_credits'
            report['credits_needed'] = credits_needed
            report['current_balance'] = current_balance
    
    return report

def get_credit_balance() -> float:
    """Get current credit balance"""
    return credit_manager.get_balance()

def add_credits(amount: float, reason: str = 'Manual addition'):
    """Add credits to user account"""
    credit_manager.add_credits(amount, reason)

def get_usage_statistics() -> Dict[str, Any]:
    """Get detailed usage statistics"""
    return credit_manager.get_usage_stats()

def check_sufficient_credits(estimated_credits: float = 5.0) -> bool:
    """Check if user has sufficient credits for generation"""
    return credit_manager.get_balance() >= estimated_credits

if __name__ == '__main__':
    # Test the monitoring system
    print("🧪 Testing Computing Monitor...")
    
    start_monitoring('reel')
    time.sleep(10)  # Simulate 10 seconds of processing
    report = stop_monitoring_and_deduct_credits()
    
    print("\n📊 COMPUTING REPORT:")
    print("=" * 50)
    print(json.dumps(report, indent=2))
    
    print(f"\n💰 Current Balance: {get_credit_balance()}")
    print(f"📈 Usage Stats: {get_usage_statistics()}")
