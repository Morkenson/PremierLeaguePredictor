"""
Scheduler service for daily data updates
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self, data_service, prediction_service):
        self.scheduler = AsyncIOScheduler()
        self.data_service = data_service
        self.prediction_service = prediction_service
        self.is_running = False
    
    async def daily_update_job(self):
        """Job that runs daily to update data and retrain model"""
        try:
            logger.info(f"🔄 Starting scheduled daily update at {datetime.now().isoformat()}")
            
            # Refresh data from API
            success = await self.data_service.refresh_data()
            
            if success:
                # Retrain model with new data
                try:
                    training_data = self.data_service.get_training_data()
                    if len(training_data) > 0:
                        await self.prediction_service.initialize_model()
                        logger.info("✅ Model retrained with new data")
                    else:
                        logger.warning("⚠️  No training data available, skipping model retrain")
                except Exception as e:
                    logger.error(f"❌ Error retraining model: {e}")
            
            logger.info(f"✅ Daily update completed at {datetime.now().isoformat()}")
            
        except Exception as e:
            logger.error(f"❌ Error in daily update job: {e}")
    
    def start_scheduler(self):
        """Start the scheduler with daily update job"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        # Schedule daily update at 3:00 AM UTC (adjust timezone as needed)
        # You can change the hour/minute by modifying the cron expression
        # Format: minute, hour, day, month, day_of_week
        self.scheduler.add_job(
            self.daily_update_job,
            trigger=CronTrigger(hour=3, minute=0),  # 3:00 AM daily
            id='daily_data_update',
            name='Daily Premier League Data Update',
            replace_existing=True,
            max_instances=1
        )
        
        self.scheduler.start()
        self.is_running = True
        logger.info("✅ Scheduler started - Daily updates scheduled for 3:00 AM UTC")
        logger.info("📅 Next run: " + str(self.scheduler.get_job('daily_data_update').next_run_time))
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler stopped")
    
    def get_next_run_time(self):
        """Get the next scheduled run time"""
        job = self.scheduler.get_job('daily_data_update')
        if job:
            return job.next_run_time
        return None
    
    async def trigger_manual_update(self):
        """Manually trigger an update (for testing or manual refresh)"""
        try:
            logger.info(f"🔄 Starting manual data update at {datetime.now().isoformat()}")
            
            # Refresh data from API
            success = await self.data_service.refresh_data()
            
            if success:
                # Retrain model with new data
                try:
                    training_data = self.data_service.get_training_data()
                    if len(training_data) > 0:
                        await self.prediction_service.initialize_model()
                        logger.info("✅ Model retrained with new data")
                    else:
                        logger.warning("⚠️  No training data available, skipping model retrain")
                except Exception as e:
                    logger.error(f"❌ Error retraining model: {e}")
            
            logger.info(f"✅ Manual update completed at {datetime.now().isoformat()}")
            return success
            
        except Exception as e:
            logger.error(f"❌ Error in manual update: {e}")
            return False

