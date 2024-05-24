# so_well/search/routes.py

def sanitize_query(query):
    if query:
        return ' & '.join(query.split())
    return ''
