    return ' '.join([x.capitalize() if x not in ['of', 'as', 'the'] else x for x in s.split('_')])
    cursor.execute('''
SELECT "name"
  FROM "organization";
''')
    organizations = cursor.fetchall()
    organizations = [{'label': x[0], 'value': x[0]} for x in organizations]
    cursor.execute('''
SELECT "name"
  FROM "language";
''')
    languages = cursor.fetchall()
    languages = [{'label': x[0], 'value': x[0]} for x in languages]
    return render_template('projects/projects.html', organization_types=organization_types, organizations=organizations, languages=languages)