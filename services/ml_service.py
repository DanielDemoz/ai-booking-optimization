"""
Machine Learning Service for No-Show Prediction
"""

import os
import pickle
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sqlalchemy import create_engine
import joblib

logger = logging.getLogger(__name__)

class MLService:
    """Machine Learning service for no-show prediction"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.model_path = os.getenv('ML_MODEL_PATH', 'models/no_show_model.pkl')
        self.retrain_threshold = int(os.getenv('RETRAIN_THRESHOLD', 100))
        
        # Load existing model if available
        self.load_model()
    
    def prepare_features(self, appointment):
        """Prepare features for ML model from appointment data"""
        features = {}
        
        # Time-based features
        features['booking_lead_time_hours'] = self._calculate_lead_time(appointment)
        features['day_of_week'] = appointment.appointment_time.weekday()
        features['time_of_day'] = appointment.appointment_time.hour + appointment.appointment_time.minute / 60.0
        
        # Patient history features
        features['previous_no_shows'] = self._get_previous_no_shows(appointment.patient_id)
        features['appointment_frequency'] = self._get_appointment_frequency(appointment.patient_id)
        
        # Appointment type features
        features['appointment_type_encoded'] = self._encode_appointment_type(appointment.appointment_type)
        
        # Weather features (simplified - in production, integrate with weather API)
        features['weather_condition_encoded'] = self._encode_weather_condition(appointment.weather_condition)
        
        # Seasonal features
        features['month'] = appointment.appointment_time.month
        features['is_weekend'] = 1 if appointment.appointment_time.weekday() >= 5 else 0
        
        return features
    
    def _calculate_lead_time(self, appointment):
        """Calculate hours between booking and appointment"""
        if appointment.created_at and appointment.appointment_time:
            delta = appointment.appointment_time - appointment.created_at
            return delta.total_seconds() / 3600
        return 24  # Default to 24 hours
    
    def _get_previous_no_shows(self, patient_id):
        """Get count of previous no-shows for patient"""
        # This would query the database in a real implementation
        # For now, return a mock value
        return 0
    
    def _get_appointment_frequency(self, patient_id):
        """Get appointment frequency (appointments per month) for patient"""
        # This would query the database in a real implementation
        # For now, return a mock value
        return 1.0
    
    def _encode_appointment_type(self, appointment_type):
        """Encode appointment type as numeric"""
        if appointment_type not in self.label_encoders:
            self.label_encoders['appointment_type'] = LabelEncoder()
            # In production, fit this on all possible appointment types
            self.label_encoders['appointment_type'].fit(['consultation', 'follow_up', 'treatment', 'emergency'])
        
        try:
            return self.label_encoders['appointment_type'].transform([appointment_type])[0]
        except ValueError:
            return 0  # Default encoding
    
    def _encode_weather_condition(self, weather_condition):
        """Encode weather condition as numeric"""
        if weather_condition not in self.label_encoders:
            self.label_encoders['weather_condition'] = LabelEncoder()
            self.label_encoders['weather_condition'].fit(['sunny', 'rainy', 'snowy', 'cloudy', 'unknown'])
        
        try:
            return self.label_encoders['weather_condition'].transform([weather_condition])[0]
        except ValueError:
            return 4  # Default to 'unknown'
    
    def create_training_data(self):
        """Create training dataset from historical appointments"""
        # In a real implementation, this would query the database
        # For now, create synthetic training data
        
        np.random.seed(42)
        n_samples = 1000
        
        # Generate synthetic features
        data = {
            'booking_lead_time_hours': np.random.exponential(48, n_samples),  # Most bookings within 48 hours
            'day_of_week': np.random.randint(0, 7, n_samples),
            'time_of_day': np.random.normal(14, 4, n_samples),  # Peak around 2 PM
            'previous_no_shows': np.random.poisson(0.5, n_samples),
            'appointment_frequency': np.random.exponential(2, n_samples),
            'appointment_type_encoded': np.random.randint(0, 4, n_samples),
            'weather_condition_encoded': np.random.randint(0, 5, n_samples),
            'month': np.random.randint(1, 13, n_samples),
            'is_weekend': np.random.randint(0, 2, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Create realistic no-show probabilities based on features
        no_show_prob = (
            0.1 +  # Base probability
            0.05 * (df['previous_no_shows'] > 2) +  # Higher if previous no-shows
            0.03 * (df['booking_lead_time_hours'] > 168) +  # Higher if booked far in advance
            0.02 * (df['is_weekend'] == 1) +  # Slightly higher on weekends
            0.01 * (df['time_of_day'] < 9) +  # Higher for early morning appointments
            0.01 * (df['time_of_day'] > 17)  # Higher for late afternoon appointments
        )
        
        # Add some randomness
        no_show_prob += np.random.normal(0, 0.02, n_samples)
        no_show_prob = np.clip(no_show_prob, 0, 1)
        
        # Generate binary labels
        df['no_show'] = (np.random.random(n_samples) < no_show_prob).astype(int)
        
        return df
    
    def train_model(self, training_data=None):
        """Train the no-show prediction model"""
        try:
            if training_data is None:
                training_data = self.create_training_data()
            
            # Prepare features and target
            feature_columns = [col for col in training_data.columns if col != 'no_show']
            X = training_data[feature_columns]
            y = training_data['no_show']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                class_weight='balanced'  # Handle class imbalance
            )
            
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            logger.info(f"Model trained successfully. Accuracy: {accuracy:.3f}")
            logger.info(f"Classification Report:\n{classification_report(y_test, y_pred)}")
            
            # Save model
            self.save_model()
            
            return {
                'success': True,
                'accuracy': accuracy,
                'training_samples': len(training_data),
                'feature_importance': dict(zip(feature_columns, self.model.feature_importances_))
            }
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def predict_no_show(self, appointment):
        """Predict no-show probability for a single appointment"""
        try:
            if self.model is None:
                # Return default prediction if no model is available
                return {
                    'probability': 0.15,  # Default 15% no-show rate
                    'risk_level': 'medium',
                    'recommended_actions': ['Send reminder 24 hours before', 'Confirm appointment day before']
                }
            
            # Prepare features
            features = self.prepare_features(appointment)
            feature_values = np.array([list(features.values())]).reshape(1, -1)
            
            # Scale features
            feature_values_scaled = self.scaler.transform(feature_values)
            
            # Predict probability
            probability = self.model.predict_proba(feature_values_scaled)[0][1]  # Probability of no-show
            
            # Determine risk level
            if probability < 0.1:
                risk_level = 'low'
                recommended_actions = ['Standard reminder 24 hours before']
            elif probability < 0.25:
                risk_level = 'medium'
                recommended_actions = ['Send reminder 48 hours before', 'Confirm appointment day before']
            else:
                risk_level = 'high'
                recommended_actions = [
                    'Send reminder 72 hours before',
                    'Confirm appointment 2 days before',
                    'Send final reminder day before',
                    'Consider calling patient directly'
                ]
            
            return {
                'probability': round(probability, 3),
                'risk_level': risk_level,
                'recommended_actions': recommended_actions
            }
            
        except Exception as e:
            logger.error(f"Error predicting no-show: {str(e)}")
            return {
                'probability': 0.15,
                'risk_level': 'medium',
                'recommended_actions': ['Send reminder 24 hours before']
            }
    
    def get_high_risk_appointments(self):
        """Get list of high-risk appointments"""
        # This would query the database in a real implementation
        # For now, return mock data
        return [
            {
                'appointment_id': 1,
                'patient_name': 'John Doe',
                'appointment_time': '2024-01-15T10:00:00',
                'risk_level': 'high',
                'probability': 0.35
            },
            {
                'appointment_id': 2,
                'patient_name': 'Jane Smith',
                'appointment_time': '2024-01-16T14:30:00',
                'risk_level': 'high',
                'probability': 0.28
            }
        ]
    
    def retrain_model(self):
        """Retrain the model with new data"""
        try:
            # Check if retraining is needed
            # In production, this would check the number of new appointments since last training
            
            result = self.train_model()
            return result
            
        except Exception as e:
            logger.error(f"Error retraining model: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def save_model(self):
        """Save the trained model to disk"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'label_encoders': self.label_encoders,
                'training_date': datetime.now(),
                'feature_columns': [
                    'booking_lead_time_hours', 'day_of_week', 'time_of_day',
                    'previous_no_shows', 'appointment_frequency', 'appointment_type_encoded',
                    'weather_condition_encoded', 'month', 'is_weekend'
                ]
            }
            
            joblib.dump(model_data, self.model_path)
            logger.info(f"Model saved to {self.model_path}")
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
    
    def load_model(self):
        """Load the trained model from disk"""
        try:
            if os.path.exists(self.model_path):
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.label_encoders = model_data['label_encoders']
                logger.info(f"Model loaded from {self.model_path}")
            else:
                logger.info("No existing model found. Will train new model.")
                
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self.model = None
    
    def get_model_info(self):
        """Get information about the current model"""
        if self.model is None:
            return {
                'status': 'no_model',
                'message': 'No model is currently loaded'
            }
        
        return {
            'status': 'loaded',
            'model_type': type(self.model).__name__,
            'feature_count': len(self.model.feature_importances_),
            'feature_importance': dict(zip(
                ['booking_lead_time_hours', 'day_of_week', 'time_of_day',
                 'previous_no_shows', 'appointment_frequency', 'appointment_type_encoded',
                 'weather_condition_encoded', 'month', 'is_weekend'],
                self.model.feature_importances_
            ))
        }

