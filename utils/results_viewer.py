import json
import os
from utils.output_manager import output_manager

def view_person_details(filename: str):
    """View detailed information for a specific person."""
    data = output_manager.load_person_data(filename)
    
    if not data:
        print(f"❌ Could not load data from {filename}")
        return
    
    metadata = data.get('metadata', {})
    linkedin = data.get('linkedin_profile', {})
    conversation = data.get('conversation', {})
    summary = data.get('summary', {})
    
    print("=" * 70)
    print(f"📊 DETAILED ANALYSIS: {metadata.get('actual_name', 'Unknown')}")
    print("=" * 70)
    
    # Metadata section
    print("\n📋 METADATA:")
    print(f"   Name: {metadata.get('actual_name', 'Unknown')}")
    print(f"   Search Query: {metadata.get('search_query', 'N/A')}")
    print(f"   Conversation Date: {metadata.get('conversation_date', 'N/A')}")
    print(f"   Analysis Date: {metadata.get('analysis_timestamp', 'N/A')[:19]}")
    
    # LinkedIn section
    print("\n🔗 LINKEDIN PROFILE:")
    print(f"   URL: {linkedin.get('url', 'Not found')}")
    if linkedin.get('profile_data'):
        profile = linkedin['profile_data']
        person_data = profile.get('person', {})
        print(f"   Full Name: {person_data.get('firstName', '')} {person_data.get('lastName', '')}")
        print(f"   Headline: {person_data.get('headline', 'N/A')}")
        print(f"   Location: {person_data.get('location', {}).get('city', 'N/A')}")
        print(f"   Connections: {person_data.get('connectionsCount', 'N/A')}")
    
    # Conversation analysis
    print("\n💬 CONVERSATION ANALYSIS:")
    analysis_text = conversation.get('analysis', {}).get('analysis', 'No analysis available')
    print(f"   {analysis_text[:500]}..." if len(analysis_text) > 500 else analysis_text)
    
    # Action items
    action_items = conversation.get('analysis', {}).get('action_items', [])
    if action_items:
        print("\n✅ ACTION ITEMS:")
        for i, item in enumerate(action_items, 1):
            print(f"   {i}. {item}")
    
    # Original conversation
    original = conversation.get('original_text', '')
    if original:
        print("\n📝 ORIGINAL CONVERSATION:")
        print(f"   {original[:300]}..." if len(original) > 300 else original)

def interactive_viewer():
    """Interactive viewer for saved analyses."""
    while True:
        print("\n" + "=" * 50)
        print("📁 CONVERSATION ANALYSIS VIEWER")
        print("=" * 50)
        print("1. List all saved analyses")
        print("2. Search analyses")
        print("3. View detailed analysis")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            analyses = output_manager.list_saved_analyses()
            if analyses:
                print(f"\n📋 Found {len(analyses)} saved analyses:")
                for i, analysis in enumerate(analyses, 1):
                    print(f"{i:2}. {analysis.get('person_name', 'Unknown')} - {analysis.get('company', 'No company')} ({analysis.get('filename', '')})")
            else:
                print("No saved analyses found.")
        
        elif choice == '2':
            search_term = input("Enter search term: ").strip()
            if search_term:
                matching = output_manager.search_saved_analyses(search_term)
                if matching:
                    print(f"\n🔍 Found {len(matching)} matching analyses:")
                    for i, analysis in enumerate(matching, 1):
                        print(f"{i:2}. {analysis.get('person_name', 'Unknown')} - {analysis.get('company', 'No company')} ({analysis.get('filename', '')})")
                else:
                    print(f"No analyses found matching '{search_term}'")
        
        elif choice == '3':
            filename = input("Enter filename (e.g., Matthew_Young_20241225_143022.json): ").strip()
            if filename:
                view_person_details(filename)
        
        elif choice == '4':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    interactive_viewer()