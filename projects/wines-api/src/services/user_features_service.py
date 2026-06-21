import logging
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import Counter
from scipy import stats

class UserFeaturesService:
    """
    Service to calculate 55 user features for the Two Tower Model.
    Features are calculated on-the-fly from user's rating history.
    
    Feature Categories:
    1. Basic User Statistics (8 features)
    2. Wine Type Preferences (6 features)
    3. Wine Attribute Preferences (25 features)
    4. Rating Behavior Patterns (8 features)
    5. Preference Diversity Metrics (4 features)
    6. Temporal Rating Patterns (4 features)
    """
    
    def __init__(self):
        logging.info("UserFeaturesService initialized")
    
    def calculate_features(
        self, 
        user_id: str, 
        ratings_data: List[Dict[str, Any]],
        preferences_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """
        Calculate all 55 features for a user based on their rating history.
        
        Args:
            user_id: User identifier
            ratings_data: List of dicts with keys: 
                {wine_id, rating, wine_type, body, abv, country, grape, 
                 complexity, is_reserve, is_grand, acidity, created_at}
            preferences_data: Optional dict from onboarding preferences
            
        Returns:
            Dict with 55 feature keys and their values
        """
        logging.info(f"Calculating features for user {user_id} with {len(ratings_data)} ratings")
        
        # Handle new users with no ratings
        if not ratings_data or len(ratings_data) == 0:
            return self._get_default_features(preferences_data)
        
        features = {}
        
        # Extract rating values for calculations
        ratings = [r['rating'] for r in ratings_data if 'rating' in r]
        
        # 1. Basic User Statistics (8 features)
        features.update(self._calculate_basic_statistics(ratings, ratings_data))
        
        # 2. Wine Type Preferences (6 features)
        features.update(self._calculate_wine_type_preferences(ratings_data))
        
        # 3. Wine Attribute Preferences (25 features)
        features.update(self._calculate_attribute_preferences(ratings_data))
        
        # 4. Rating Behavior Patterns (8 features)
        features.update(self._calculate_rating_patterns(ratings))
        
        # 5. Preference Diversity Metrics (4 features)
        features.update(self._calculate_diversity_metrics(ratings))
        
        # 6. Temporal Rating Patterns (4 features)
        features.update(self._calculate_temporal_patterns(ratings_data))
        
        logging.info(f"Calculated {len(features)} features for user {user_id}")
        return features
    
    def _calculate_basic_statistics(self, ratings: List[float], ratings_data: List[Dict]) -> Dict[str, float]:
        """Calculate 8 basic user statistics."""
        if not ratings:
            return {
                'rating_mean': 0.0,
                'rating_std': 0.0,
                'rating_count': 0,
                'rating_min': 0.0,
                'rating_max': 0.0,
                'wines_tried': 0,
                'avg_ratings_per_wine': 0.0,
                'coefficient_of_variation': 0.0
            }
        
        ratings_array = np.array(ratings)
        unique_wines = len(set(r.get('wine_id') for r in ratings_data if r.get('wine_id')))
        
        mean = float(np.mean(ratings_array))
        std = float(np.std(ratings_array))
        
        return {
            'rating_mean': mean,
            'rating_std': std,
            'rating_count': len(ratings),
            'rating_min': float(np.min(ratings_array)),
            'rating_max': float(np.max(ratings_array)),
            'wines_tried': unique_wines,
            'avg_ratings_per_wine': len(ratings) / unique_wines if unique_wines > 0 else 0.0,
            'coefficient_of_variation': std / mean if mean > 0 else 0.0
        }
    
    def _calculate_wine_type_preferences(self, ratings_data: List[Dict]) -> Dict[str, float]:
        """Calculate 6 wine type preferences using weighted averages."""
        wine_types = {
            'red_wine_preference': ['Red', 'red'],
            'white_wine_preference': ['White', 'white'],
            'sparkling_wine_preference': ['Sparkling', 'sparkling'],
            'rose_wine_preference': ['Rose', 'Rosé', 'rose', 'rosé'],
            'dessert_wine_preference': ['Dessert', 'dessert', 'Sweet', 'sweet'],
            'dessert_port_wine_preference': ['Port', 'port', 'Dessert Port', 'dessert port']
        }
        
        preferences = {}
        for pref_name, type_variations in wine_types.items():
            type_ratings = [
                r['rating'] for r in ratings_data 
                if r.get('wine_type') in type_variations
            ]
            preferences[pref_name] = float(np.mean(type_ratings)) if type_ratings else 0.0
        
        return preferences
    
    def _calculate_attribute_preferences(self, ratings_data: List[Dict]) -> Dict[str, float]:
        """Calculate 25 wine attribute preferences."""
        features = {}
        
        # ABV Preferences (3 features)
        abv_ratings = [(r['rating'], r.get('abv', 0)) for r in ratings_data if r.get('abv')]
        if abv_ratings:
            ratings, abvs = zip(*abv_ratings)
            features['weighted_abv_preference'] = float(np.average(abvs, weights=ratings))
            features['avg_abv_tried'] = float(np.mean(abvs))
            
            # High vs Low ABV preference
            high_abv = [r for r, a in abv_ratings if a >= 13.5]
            low_abv = [r for r, a in abv_ratings if a < 13.5]
            features['high_vs_low_abv_preference'] = (
                (np.mean(high_abv) if high_abv else 0) - 
                (np.mean(low_abv) if low_abv else 0)
            )
        else:
            features['weighted_abv_preference'] = 0.0
            features['avg_abv_tried'] = 0.0
            features['high_vs_low_abv_preference'] = 0.0
        
        # Body Type Preferences (5 features)
        body_types = {
            'very_light_bodied_preference': ['Very Light', 'very light', '1'],
            'light_bodied_preference': ['Light', 'light', '2'],
            'medium_bodied_preference': ['Medium', 'medium', '3'],
            'full_bodied_preference': ['Full', 'full', '4'],
            'very_full_bodied_preference': ['Very Full', 'very full', '5']
        }
        for pref_name, body_variations in body_types.items():
            body_ratings = [
                r['rating'] for r in ratings_data 
                if str(r.get('body', '')).lower() in [v.lower() for v in body_variations]
            ]
            features[pref_name] = float(np.mean(body_ratings)) if body_ratings else 0.0
        
        # Acidity Preferences (3 features)
        acidity_types = {
            'low_acidity_preference': ['Low', 'low', '1'],
            'medium_acidity_preference': ['Medium', 'medium', '2'],
            'high_acidity_preference': ['High', 'high', '3']
        }
        for pref_name, acidity_variations in acidity_types.items():
            acidity_ratings = [
                r['rating'] for r in ratings_data 
                if str(r.get('acidity', '')).lower() in [v.lower() for v in acidity_variations]
            ]
            features[pref_name] = float(np.mean(acidity_ratings)) if acidity_ratings else 0.0
        
        # Top Country Preferences (5 features)
        country_ratings = {}
        for r in ratings_data:
            country = r.get('country')
            if country:
                if country not in country_ratings:
                    country_ratings[country] = []
                country_ratings[country].append(r['rating'])
        
        # Sort countries by rating count, take top 5
        top_countries = sorted(
            country_ratings.items(), 
            key=lambda x: len(x[1]), 
            reverse=True
        )[:5]
        
        for i in range(5):
            if i < len(top_countries):
                country, ratings = top_countries[i]
                features[f'country_{i+1}_preference'] = float(np.mean(ratings))
            else:
                features[f'country_{i+1}_preference'] = 0.0
        
        # Top Grape Preferences (5 features)
        grape_ratings = {}
        for r in ratings_data:
            grape = r.get('grape')
            if grape:
                if grape not in grape_ratings:
                    grape_ratings[grape] = []
                grape_ratings[grape].append(r['rating'])
        
        # Sort grapes by rating count, take top 5
        top_grapes = sorted(
            grape_ratings.items(), 
            key=lambda x: len(x[1]), 
            reverse=True
        )[:5]
        
        for i in range(5):
            if i < len(top_grapes):
                grape, ratings = top_grapes[i]
                features[f'grape_{i+1}_preference'] = float(np.mean(ratings))
            else:
                features[f'grape_{i+1}_preference'] = 0.0
        
        # Complexity & Quality (4 features)
        complex_ratings = [r['rating'] for r in ratings_data if r.get('complexity', 0) > 0]
        simple_ratings = [r['rating'] for r in ratings_data if r.get('complexity', 0) == 0]
        features['complexity_preference'] = (
            (np.mean(complex_ratings) if complex_ratings else 0) - 
            (np.mean(simple_ratings) if simple_ratings else 0)
        )
        
        complexity_values = [r.get('complexity', 0) for r in ratings_data if r.get('complexity')]
        features['avg_complexity_tried'] = float(np.mean(complexity_values)) if complexity_values else 0.0
        
        reserve_ratings = [r['rating'] for r in ratings_data if r.get('is_reserve', False)]
        non_reserve_ratings = [r['rating'] for r in ratings_data if not r.get('is_reserve', False)]
        features['reserve_preference'] = (
            (np.mean(reserve_ratings) if reserve_ratings else 0) - 
            (np.mean(non_reserve_ratings) if non_reserve_ratings else 0)
        )
        
        grand_ratings = [r['rating'] for r in ratings_data if r.get('is_grand', False)]
        non_grand_ratings = [r['rating'] for r in ratings_data if not r.get('is_grand', False)]
        features['grand_preference'] = (
            (np.mean(grand_ratings) if grand_ratings else 0) - 
            (np.mean(non_grand_ratings) if non_grand_ratings else 0)
        )
        
        return features
    
    def _calculate_rating_patterns(self, ratings: List[float]) -> Dict[str, float]:
        """Calculate 8 rating behavior pattern features."""
        if not ratings:
            return {
                'high_rating_proportion': 0.0,
                'low_rating_proportion': 0.0,
                'rating_entropy': 0.0,
                'rating_1_proportion': 0.0,
                'rating_2_proportion': 0.0,
                'rating_3_proportion': 0.0,
                'rating_4_proportion': 0.0,
                'rating_5_proportion': 0.0
            }
        
        total = len(ratings)
        rating_counts = Counter(ratings)
        
        # Calculate proportions
        proportions = {}
        for i in range(1, 6):
            proportions[f'rating_{i}_proportion'] = rating_counts.get(float(i), 0) / total
        
        # High (4-5) and Low (1-2) rating proportions
        high_count = sum(1 for r in ratings if r >= 4)
        low_count = sum(1 for r in ratings if r <= 2)
        
        proportions['high_rating_proportion'] = high_count / total
        proportions['low_rating_proportion'] = low_count / total
        
        # Rating entropy (distribution diversity)
        probs = [count / total for count in rating_counts.values() if count > 0]
        entropy = -sum(p * np.log2(p) for p in probs) if probs else 0.0
        proportions['rating_entropy'] = float(entropy)
        
        return proportions
    
    def _calculate_diversity_metrics(self, ratings: List[float]) -> Dict[str, float]:
        """Calculate 4 preference diversity metrics."""
        if not ratings or len(ratings) < 2:
            return {
                'rating_range': 0.0,
                'rating_variance': 0.0,
                'unique_ratings_count': 0,
                'rating_skewness': 0.0
            }
        
        ratings_array = np.array(ratings)
        
        return {
            'rating_range': float(np.max(ratings_array) - np.min(ratings_array)),
            'rating_variance': float(np.var(ratings_array)),
            'unique_ratings_count': len(set(ratings)),
            'rating_skewness': float(stats.skew(ratings_array)) if len(ratings) > 2 else 0.0
        }
    
    def _calculate_temporal_patterns(self, ratings_data: List[Dict]) -> Dict[str, float]:
        """Calculate 4 temporal rating pattern features."""
        # Extract timestamps
        dates = []
        for r in ratings_data:
            created_at = r.get('created_at')
            if created_at:
                if isinstance(created_at, str):
                    try:
                        dates.append(datetime.fromisoformat(created_at.replace('Z', '+00:00')))
                    except:
                        pass
                elif isinstance(created_at, datetime):
                    dates.append(created_at)
        
        if len(dates) < 2:
            return {
                'date_range_days': 0.0,
                'avg_days_between_ratings': 0.0,
                'rating_trend': 0.0,
                'rating_frequency': 0.0
            }
        
        # Sort dates
        dates.sort()
        
        # Calculate date range
        date_range = (dates[-1] - dates[0]).days
        
        # Calculate average days between ratings
        if len(dates) > 1:
            time_diffs = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
            avg_days_between = np.mean(time_diffs) if time_diffs else 0.0
        else:
            avg_days_between = 0.0
        
        # Calculate rating trend (linear regression slope)
        ratings_with_dates = [
            (r['rating'], r.get('created_at')) 
            for r in ratings_data 
            if r.get('created_at')
        ]
        
        if len(ratings_with_dates) > 2:
            # Convert to timestamps for regression
            timestamps = []
            ratings_for_trend = []
            for rating, date in ratings_with_dates:
                if isinstance(date, str):
                    try:
                        dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
                        timestamps.append(dt.timestamp())
                        ratings_for_trend.append(rating)
                    except:
                        pass
                elif isinstance(date, datetime):
                    timestamps.append(date.timestamp())
                    ratings_for_trend.append(rating)
            
            if len(timestamps) > 2:
                slope, _ = np.polyfit(timestamps, ratings_for_trend, 1)
                rating_trend = float(slope)
            else:
                rating_trend = 0.0
        else:
            rating_trend = 0.0
        
        # Rating frequency (ratings per day)
        rating_frequency = len(dates) / date_range if date_range > 0 else 0.0
        
        return {
            'date_range_days': float(date_range),
            'avg_days_between_ratings': float(avg_days_between),
            'rating_trend': rating_trend,
            'rating_frequency': float(rating_frequency)
        }
    
    def _get_default_features(self, preferences_data: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        """
        Return default features for new users with no ratings.
        Can optionally use onboarding preferences if available.
        """
        logging.info("Generating default features for new user")
        
        # Start with neutral defaults
        defaults = {
            # Basic Statistics
            'rating_mean': 3.0,
            'rating_std': 0.0,
            'rating_count': 0,
            'rating_min': 0.0,
            'rating_max': 0.0,
            'wines_tried': 0,
            'avg_ratings_per_wine': 0.0,
            'coefficient_of_variation': 0.0,
            
            # Wine Type Preferences
            'red_wine_preference': 3.0,
            'white_wine_preference': 3.0,
            'sparkling_wine_preference': 3.0,
            'rose_wine_preference': 3.0,
            'dessert_wine_preference': 3.0,
            'dessert_port_wine_preference': 3.0,
            
            # ABV Preferences
            'weighted_abv_preference': 12.5,
            'avg_abv_tried': 12.5,
            'high_vs_low_abv_preference': 0.0,
            
            # Body Preferences
            'very_light_bodied_preference': 3.0,
            'light_bodied_preference': 3.0,
            'medium_bodied_preference': 3.0,
            'full_bodied_preference': 3.0,
            'very_full_bodied_preference': 3.0,
            
            # Acidity Preferences
            'low_acidity_preference': 3.0,
            'medium_acidity_preference': 3.0,
            'high_acidity_preference': 3.0,
            
            # Top Countries (neutral)
            'country_1_preference': 3.0,
            'country_2_preference': 3.0,
            'country_3_preference': 3.0,
            'country_4_preference': 3.0,
            'country_5_preference': 3.0,
            
            # Top Grapes (neutral)
            'grape_1_preference': 3.0,
            'grape_2_preference': 3.0,
            'grape_3_preference': 3.0,
            'grape_4_preference': 3.0,
            'grape_5_preference': 3.0,
            
            # Complexity & Quality
            'complexity_preference': 0.0,
            'avg_complexity_tried': 0.0,
            'reserve_preference': 0.0,
            'grand_preference': 0.0,
            
            # Rating Patterns
            'high_rating_proportion': 0.0,
            'low_rating_proportion': 0.0,
            'rating_entropy': 0.0,
            'rating_1_proportion': 0.0,
            'rating_2_proportion': 0.0,
            'rating_3_proportion': 0.0,
            'rating_4_proportion': 0.0,
            'rating_5_proportion': 0.0,
            
            # Diversity Metrics
            'rating_range': 0.0,
            'rating_variance': 0.0,
            'unique_ratings_count': 0,
            'rating_skewness': 0.0,
            
            # Temporal Patterns
            'date_range_days': 0.0,
            'avg_days_between_ratings': 0.0,
            'rating_trend': 0.0,
            'rating_frequency': 0.0
        }
        
        # TODO: Override with preferences_data if available
        # This could use onboarding preferences to seed initial values
        
        return defaults
