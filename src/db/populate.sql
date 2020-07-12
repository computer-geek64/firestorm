-- populate.sql
-- Insert into table organization_type
INSERT INTO "organization_type" (
                "label"
            )
     VALUES (
                'personal'
            ),
            (
                'school'
            ),
            (
                'work'
            ),
            (
                'hackathon'
            );

-- Insert into table organization
INSERT INTO "organization" (
                "name",
                "type"
            )
     VALUES (
                'Personal',
                'personal'
            ),
            (
                'Georgia Tech',
                'school'
            ),
            (
                'Nead Werx',
                'work'
            ),
            (
                'HackGT',
                'hackathon'
            ),
            (
                'SwampHacks',
                'hackathon'
            ),
            (
                'OSCAR',
                'work'
            );

-- Insert into table language
INSERT INTO "language" (
                "name",
                "extension",
                "color"
            )
     VALUES (
                'Python',
                'py',
                '#3572a5'
            ),
            (
                'Java',
                'java',
                '#b07219'
            ),
            (
                'Ruby',
                'rb',
                '#701516'
            ),
            (
                'Shell',
                'sh',
                '#89e051'
            ),
            (
                'HTML',
                'html',
                '#e34c26'
            ),
            (
                'CSS',
                'css',
                '#563d7c'
            ),
            (
                'JavaScript',
                'js',
                '#f1e05a'
            );