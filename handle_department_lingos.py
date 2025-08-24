dept_lingos = {
    'aerospace engineering': [
        'aero', 'aerospace', 'ae', 'aero engg', 'aero eng', 'aero dept', 'aerospace dept',
        'aero department', 'aerospace engineering', 'aeronautical', 'aeronautics'
    ],
    'chemical engineering': [
        'chem engg', 'chem eng', 'che', 'chem', 'chemical', 'chem dept', 'chemical dept',
        'chemical engineering', 'chemical eng', 'chemistry engg', 'che engg'
    ],
    'climate studies': [
        'climate', 'climate studies', 'climate sci', 'climate dept', 'climate department',
        'csu', 'climate engg'
    ],
    'computer science and engineering': [
        'cse', 'cs', 'comp sci', 'computer science', 'cs engg', 'cs eng', 'cs dept',
        'comp science', 'comp engg', 'computers dept', 'cse dept', 'comps'
    ],
    'industrial design': [
        'idc', 'ind design', 'industrial design', 'design dept', 'design department'
    ],
    'centre for digital health': [
        'cdh', 'digital health', 'health tech', 'digital healthcare', 'dig health'
    ],
    'centre for machine intelligence and data science': [
        'cminds', 'machine intelligence', 'ai dept', 'data science', 'ml dept',
        'c-minds', 'machine learning', 'artificial intelligence', 'datasci'
    ],
    'economics': [
        'eco', 'economics', 'eco dept', 'economics dept', 'economics department'
    ],
    'electrical engineering': [
        'ee', 'electrical', 'elec', 'elec engg', 'elec eng', 'ee dept', 'electrical dept',
        'electrical engineering', 'electrical eng', 'elektical', 'elec department'
    ],
    'energy science and engineering': [
        'ese', 'energy engg', 'energy sci', 'energy science', 'energy dept',
        'energy sciences', 'energy engineering'
    ],
    'bioscience and bioengineering': [
        'bio', 'bio engg', 'bsbe', 'bio sciences', 'bio sci', 'bio dept', 'bioengineering',
        'biotech', 'biological sciences'
    ],
    'centre for entrepreneurship': [
        'cfep', 'entrepreneurship', 'entrepreneurship centre', 'startup centre',
        'e-cell', 'entrepreneur dept'
    ],
    'engineering physics': [
        'ep', 'engg physics', 'phy engg', 'eng phy', 'engineering physics',
        'physics engg'
    ],
    'environmental science and engineering': [
        'env sci', 'ese', 'environmental engg', 'environmental science', 'env dept',
        'environment engg', 'environment sci'
    ],
    'chemistry': [
        'chem', 'chem dept', 'chemistry', 'chemistry dept', 'chemistry department'
    ],
    'educational technology': [
        'ed tech', 'educational tech', 'edutech', 'edu tech', 'education technology'
    ],
    'centre of studies in resources engineering': [
        'csre', 'resources engg', 'resources engineering', 'resources dept'
    ],
    'applied geophysics': [
        'geo', 'applied geo', 'geophysics', 'geo phys', 'geo dept', 'applied geophysics'
    ],
    'earth sciences': [
        'earth sci', 'es', 'geology', 'earth dept', 'earth science', 'geological sciences'
    ],
    'humanities and social sciences': [
        'hss', 'hum', 'humanities', 'social sci', 'humanities dept', 'humanities department',
        'social sciences', 'arts dept'
    ],
    'industrial engineering and operations research': [
        'ieor', 'operations research', 'ind engg', 'ind eng', 'or', 'operations dept',
        'industrial engineering'
    ],
    'shailesh j. mehta school of management': [
        'sjmsom', 'som', 'management school', 'mba dept', 'school of management',
        'business school', 'b-school'
    ],
    'centre for liberal education (cledu)': [
        'cledu', 'liberal education', 'liberal studies', 'liberal dept'
    ],
    'mathematics': [
        'math', 'maths', 'math dept', 'math department', 'mathematics'
    ],
    'mechanical engineering': [
        'mech', 'mech engg', 'me', 'mechanical', 'mechanical dept', 'mechanical department',
        'mechnical', 'mech engineering', 'berozgar'
    ],
    'metallurgical engineering and materials science': [
        'meta', 'metallurgy', 'mems', 'materials sci', 'materials science',
        'metallurgy dept', 'metallurgical engineering'
    ],
    'centre for research in nanotechnology and science': [
        'crnts', 'nano tech', 'nanotech', 'nanotechnology', 'nano dept'
    ],
    'physics': [
        'phy', 'physics', 'physics dept', 'physics department'
    ],
    'centre for policy studies': [
        'cps', 'policy studies', 'policy centre', 'policy dept'
    ],
    'systems and control engineering': [
        'syscon', 'sce', 'systems engg', 'control engg', 'systems and control',
        'control systems'
    ],
    'applied statistics and informatics': [
        'asi', 'stats', 'statistics', 'stats dept', 'statistics dept', 'applied stats'
    ],
    'centre for technology alternatives for rural areas': [
        'ctara', 'rural tech', 'rural development centre', 'rural development'
    ],
    'centre for urban science and engineering': [
        'cuse', 'urban science', 'urban studies', 'urban engg', 'urban dept'
    ],
    'visual communication': [
        'viscom', 'visual comm', 'visual design', 'visual communication'
    ],
    'civil engineering': [
        'civil', 'ce', 'civil engg', 'civil dept', 'civil engineering', 'mistri', 'mistri department'
    ]
}

def handle_department_lingo(search_filter, query):
    if "department" in search_filter:
        dept_val = search_filter["department"].strip().lower()
    
        found_lingo = False
        for key, lingos in dept_lingos.items():
            if dept_val in lingos:
                # print(f"Found lingo: '{dept_val}' maps to '{key}'")
                # Update the filter to use the official department name
                search_filter["department"] = key
                # Append the clarification to the query for the retriever
                query += f" (Note: '{dept_val}' refers to the {key} department)"
                found_lingo = True
                break
        
        if not found_lingo:
            print("No lingo found, using department value as is.")
    return search_filter, query