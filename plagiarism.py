import streamlit as st
from googleapiclient.discovery import build
import difflib

# Function to perform Google Custom Search API query
def google_search(api_key, search_engine_id, query):
    service = build('customsearch', 'v1', developerKey=api_key)
    res = service.cse().list(q=query, cx=search_engine_id).execute()
    return res.get('items', [])

# Function to highlight similarities between input text and search results
def highlight_similarities(input_text, search_results):
    input_text_lower = input_text.lower()
    results = []
    for result in search_results:
        snippet = result.get('snippet', '').replace('<br>', ' ')
        snippet_lower = snippet.lower()

        # Using difflib to find matching lines (similarity)
        matcher = difflib.SequenceMatcher(None, input_text_lower, snippet_lower)
        match = matcher.find_longest_match(0, len(input_text_lower), 0, len(snippet_lower))

        if match.size > 0:
            start = match.b
            end = match.b + match.size
            highlighted_snippet = (
                snippet[:start] + '<span style="background-color: #FFFF00">' + snippet[start:end] + '</span>' + snippet[end:]
            )
            similarity_score = match.size / len(input_text_lower)  # Calculate similarity percentage
            results.append({
                "title": result['title'],
                "link": result['link'],
                "highlighted_snippet": highlighted_snippet,
                "similarity_percentage": similarity_score
            })

    return results

# Function to calculate similarity percentage between two files
def calculate_similarity(file1_content, file2_content):
    matcher = difflib.SequenceMatcher(None, file1_content.lower(), file2_content.lower())
    similarity_ratio = matcher.ratio()
    return similarity_ratio

# Streamlit app UI and logic
def main():
    st.title('Plagiarism Checker')

    # Option to choose between checking two files or one file against the web
    option = st.selectbox('Choose an option:', ['Check similarity between two files', 'Check one file against the web'])

    if option == 'Check similarity between two files':
        st.header('Check Similarity Between Two Files')
        
        # File uploader for the first file
        uploaded_file1 = st.file_uploader("Upload the first file", type=['txt'])
        
        # File uploader for the second file
        uploaded_file2 = st.file_uploader("Upload the second file", type=['txt'])
        
        if st.button('Check Similarity'):
            if uploaded_file1 and uploaded_file2:
                file1_content = uploaded_file1.read().decode('utf-8')
                file2_content = uploaded_file2.read().decode('utf-8')
                similarity_ratio = calculate_similarity(file1_content, file2_content)
                st.write(f"Similarity percentage between the two files: {similarity_ratio * 100:.2f}%")
            else:
                st.warning("Please upload both files.")

    elif option == 'Check one file against the web':
        st.header('Check One File Against the Web')

        uploaded_file = st.file_uploader("Upload a file", type=['txt'])
        
        if st.button('Search'):
            if uploaded_file:
                query = uploaded_file.read().decode('utf-8')
                
                # Replace with your Google API key and Custom Search Engine ID

                api_key =  'your api key'
                search_engine_id = 'your search engine id'
                
                search_results = google_search(api_key, search_engine_id, query)
                highlighted_results = highlight_similarities(query, search_results)

                for result in highlighted_results:
                    st.subheader(result['title'])
                    st.write(f"Link: {result['link']}")
                    st.write(f"Similarity Percentage: {result['similarity_percentage'] * 100:.2f}%")
                    st.markdown(result['highlighted_snippet'], unsafe_allow_html=True)
                    st.write('---')
            else:
                st.warning("Please upload a file.")

if __name__ == '__main__':
    main()
