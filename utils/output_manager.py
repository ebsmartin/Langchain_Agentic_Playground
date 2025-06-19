import os
import json
from datetime import datetime
from typing import Dict, Any
import re

class ConversationOutputManager:
    """Manages saving conversation analysis and LinkedIn profile data to organized files."""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def _sanitize_filename(self, name: str) -> str:
        """Convert a person's name into a safe filename."""
        # Remove special characters and replace spaces with underscores
        safe_name = re.sub(r'[<>:"/\\|?*]', '', name)
        safe_name = safe_name.replace(' ', '_')
        return safe_name
    
    def _extract_actual_name_from_linkedin_url(self, linkedin_url: str) -> str:
        """Extract a person's name from their LinkedIn URL if possible."""
        if not linkedin_url or 'linkedin.com/in/' not in linkedin_url:
            return None
        
        # Extract the LinkedIn username (e.g., "matthew-young-123" from URL)
        username = linkedin_url.split('/in/')[-1].split('?')[0].split('/')[0]
        
        # Convert LinkedIn username to readable name (basic attempt)
        # This is a fallback - ideally we'd get the actual name from profile data
        name_parts = username.split('-')
        if len(name_parts) >= 2:
            # Capitalize first and last name
            first_name = name_parts[0].capitalize()
            last_name = name_parts[1].capitalize()
            return f"{first_name} {last_name}"
        
        return username.replace('-', ' ').title()
    
    def _get_actual_name_from_profile_data(self, profile_data: Dict[str, Any]) -> str:
        """Extract the actual name from LinkedIn profile data."""
        if not profile_data:
            print("❌ No profile data provided")
            return None
        
        # Debug: Print what data we have
        print(f"🔍 DEBUG: Profile data keys: {list(profile_data.keys()) if isinstance(profile_data, dict) else 'Not a dict'}")
        
        # Check if we have the Scrapin API response format
        if 'person' in profile_data and isinstance(profile_data['person'], dict):
            person_data = profile_data['person']
            print(f"🔍 DEBUG: Person data keys: {list(person_data.keys())}")
            
            # Extract firstName and lastName from person object
            first_name = person_data.get('firstName', '').strip()
            last_name = person_data.get('lastName', '').strip()
            
            print(f"🔍 DEBUG: Found firstName: '{first_name}', lastName: '{last_name}'")
            
            if first_name and last_name:
                full_name = f"{first_name} {last_name}"
                print(f"✅ Extracted full name from profile data: {full_name}")
                return full_name
            elif first_name:
                print(f"✅ Found firstName only: {first_name}")
                return first_name
            elif last_name:
                print(f"✅ Found lastName only: {last_name}")
                return last_name
        
        # Try alternative field structures for different API formats
        alternative_fields = [
            'full_name', 'name', 'fullName', 'displayName',
            # Direct access patterns
            'firstName', 'lastName'
        ]
        
        for field in alternative_fields:
            if field in profile_data and isinstance(profile_data[field], str):
                name = profile_data[field].strip()
                if name:
                    print(f"✅ Found name in direct field '{field}': {name}")
                    return name
        
        # Try to construct from top-level firstName/lastName (some APIs use this)
        first = profile_data.get('firstName', '').strip()
        last = profile_data.get('lastName', '').strip()
        
        if first and last:
            full_name = f"{first} {last}"
            print(f"✅ Constructed name from top-level fields: {full_name}")
            return full_name
        elif first:
            print(f"✅ Found top-level firstName: {first}")
            return first
        
        print("❌ No name found in profile data")
        return None
    
    def _extract_info_from_conversation_analysis(self, conversation_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured info from the existing conversation analysis (NO DUPLICATION)."""
        extracted_info = {}
        
        if not conversation_analysis:
            return extracted_info
        
        analysis_text = conversation_analysis.get('analysis', '')
        
        if analysis_text:
            lines = analysis_text.split('\n')
            
            # Extract job title
            for line in lines:
                if 'Job Title/Role:' in line and ':' in line:
                    job_title = line.split(':', 1)[1].strip()
                    if job_title and job_title not in ['[Only if explicitly mentioned]', 'Not specified']:
                        extracted_info['job_title'] = job_title
                    break
            
            # Extract company
            for line in lines:
                if 'Company/Industry:' in line and ':' in line:
                    company = line.split(':', 1)[1].strip()
                    if company and company not in ['[Only if explicitly mentioned]', 'Not specified']:
                        extracted_info['company'] = company
                    break
            
            # Extract person mapping for additional names
            person_mapping = conversation_analysis.get('person_mapping', {})
            if person_mapping:
                extracted_info['person_mapping'] = person_mapping
        
        # Add action items count
        action_items = conversation_analysis.get('action_items', [])
        extracted_info['action_items_count'] = len(action_items)
        
        return extracted_info
    
    def save_conversation_analysis(
        self,
        search_query: str,
        linkedin_url: str,
        profile_data: Dict[str, Any] = None,
        conversation_analysis: Dict[str, Any] = None,
        original_conversation: str = None,
        conversation_date: str = None,
        user_identity: Dict[str, Any] = None
    ) -> str:
        """
        Save all conversation and profile data for a person.
        
        Returns:
            str: The filename where the data was saved
        """
        # Determine the actual person's name
        actual_name = None
        
        # Try to get name from profile data first (most accurate)
        if profile_data:
            actual_name = self._get_actual_name_from_profile_data(profile_data)
        
        # Fallback to extracting from LinkedIn URL
        if not actual_name and linkedin_url:
            actual_name = self._extract_actual_name_from_linkedin_url(linkedin_url)
        
        # Final fallback to using search query
        if not actual_name:
            # Use the first few words of search query as name
            query_words = search_query.split()[:2]  # Take first 2 words as likely name
            actual_name = ' '.join(query_words)
        
        # Create safe filename
        safe_filename = self._sanitize_filename(actual_name)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_filename}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        # Extract info from EXISTING conversation analysis (no duplication!)
        analysis_extracted_info = self._extract_info_from_conversation_analysis(conversation_analysis)
        
        # Create summary using EXISTING analysis results
        summary = {
            'person_name': actual_name,
            'search_used': search_query,
            'linkedin_found': bool(linkedin_url and 'linkedin.com' in linkedin_url),
            'linkedin_url': linkedin_url if linkedin_url and 'linkedin.com' in linkedin_url else None,
            **analysis_extracted_info  # Include extracted info from existing analysis
        }
        
        # Prepare the comprehensive data structure
        output_data = {
            'metadata': {
                'actual_name': actual_name,
                'search_query': search_query,
                'conversation_date': conversation_date or datetime.now().strftime('%Y-%m-%d'),
                'analysis_timestamp': datetime.now().isoformat(),
                'user_identity': user_identity
            },
            'linkedin_profile': {
                'url': linkedin_url,
                'profile_data': profile_data,
                'data_source': 'scrapin' if profile_data else 'url_only'
            },
            'conversation': {
                'original_text': original_conversation,
                'analysis': conversation_analysis  # Store the EXISTING analysis as-is
            },
            'summary': summary  # This now uses extracted info from existing analysis
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved analysis for {actual_name} to: {filename}")
        return filename
    
    def load_person_data(self, filename: str) -> Dict[str, Any]:
        """Load previously saved data for a person."""
        filepath = os.path.join(self.output_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def list_saved_analyses(self) -> list[Dict[str, Any]]:
        """List all saved conversation analyses with summaries."""
        analyses = []
        
        if not os.path.exists(self.output_dir):
            return analyses
        
        for filename in os.listdir(self.output_dir):
            if filename.endswith('.json'):
                try:
                    data = self.load_person_data(filename)
                    if data and 'summary' in data:
                        summary = data['summary'].copy()
                        summary['filename'] = filename
                        summary['file_date'] = data['metadata'].get('analysis_timestamp', '')
                        analyses.append(summary)
                except Exception as e:
                    print(f"⚠️ Error loading {filename}: {e}")
        
        # Sort by analysis date (newest first)
        analyses.sort(key=lambda x: x.get('file_date', ''), reverse=True)
        return analyses
    
    def search_saved_analyses(self, search_term: str) -> list[Dict[str, Any]]:
        """Search saved analyses by person name, company, or job title."""
        all_analyses = self.list_saved_analyses()
        search_term = search_term.lower()
        
        matching = []
        for analysis in all_analyses:
            # Search in name, company, job title
            searchable_text = ' '.join([
                analysis.get('person_name', ''),
                analysis.get('company', ''),
                analysis.get('job_title', ''),
                analysis.get('search_used', '')
            ]).lower()
            
            if search_term in searchable_text:
                matching.append(analysis)
        
        return matching

# Global instance
output_manager = ConversationOutputManager()